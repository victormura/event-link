import os
import unittest
from datetime import datetime, timedelta

# Ensure test configuration before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient
from app import models, auth
from app.api import app
from app.database import Base, engine, SessionLocal, get_db


class APITestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        def _override_get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = _override_get_db
        self.client = TestClient(app)

    def register_student(self, email: str) -> str:
        response = self.client.post(
            "/register",
            json={"email": email, "password": "password123", "confirm_password": "password123"},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def login(self, email: str, password: str) -> str:
        response = self.client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_student_registration_and_duplicate_email(self):
        first = self.client.post(
            "/register",
            json={"email": "student@test.ro", "password": "password123", "confirm_password": "password123"},
        )
        self.assertEqual(first.status_code, 200)
        duplicate = self.client.post(
            "/register",
            json={"email": "student@test.ro", "password": "password123", "confirm_password": "password123"},
        )
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("deja folosit", duplicate.json().get("detail", ""))

    def test_event_creation_and_capacity_enforced(self):
        # create organizer manually
        db = SessionLocal()
        organizer = models.User(
            email="org@test.ro",
            password_hash=auth.get_password_hash("organizer123"),
            role=models.UserRole.organizator,
        )
        db.add(organizer)
        db.commit()

        organizer_token = self.login("org@test.ro", "organizer123")

        start_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        payload = {
            "title": "Test Event",
            "description": "Descriere",
            "category": "Test",
            "start_time": start_time,
            "end_time": None,
            "location": "Online",
            "max_seats": 1,
            "tags": ["test"],
        }
        create_resp = self.client.post(
            "/api/events",
            json=payload,
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        self.assertEqual(create_resp.status_code, 201)
        event_id = create_resp.json()["id"]

        # student one registers successfully
        student1_token = self.register_student("s1@test.ro")
        reg1 = self.client.post(
            f"/api/events/{event_id}/register",
            headers={"Authorization": f"Bearer {student1_token}"},
        )
        self.assertEqual(reg1.status_code, 201)

        # student two blocked by capacity
        student2_token = self.register_student("s2@test.ro")
        reg2 = self.client.post(
            f"/api/events/{event_id}/register",
            headers={"Authorization": f"Bearer {student2_token}"},
        )
        self.assertEqual(reg2.status_code, 409)
        self.assertIn("plin", reg2.json().get("detail", ""))


if __name__ == "__main__":
    unittest.main()
