import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { EventListComponent } from './event-list/event-list.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { EventDetailsComponent } from './event-details/event-details.component';
import { EventFormComponent } from './event-form/event-form.component';
import { OrganizerEventsComponent } from './organizer-events/organizer-events.component';
import { ParticipantsComponent } from './participants/participants.component';
import { MyEventsComponent } from './my-events/my-events.component';

export const routes: Routes = [
  { path: '', component: EventListComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'events/:id', component: EventDetailsComponent },
  { path: 'events/:id/edit', component: EventFormComponent, canActivate: [authGuard], data: { role: 'organizator' } },
  { path: 'create-event', component: EventFormComponent, canActivate: [authGuard], data: { role: 'organizator' } },
  { path: 'organizer/events', component: OrganizerEventsComponent, canActivate: [authGuard], data: { role: 'organizator' } },
  { path: 'organizer/events/:id/participants', component: ParticipantsComponent, canActivate: [authGuard], data: { role: 'organizator' } },
  { path: 'my-events', component: MyEventsComponent, canActivate: [authGuard], data: { role: 'student' } },
];
