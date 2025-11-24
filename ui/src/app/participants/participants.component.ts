import { CommonModule, DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ParticipantList } from '../models';
import { EventService } from '../services/event.service';

@Component({
  selector: 'app-participants',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './participants.component.html',
  styleUrl: './participants.component.scss',
})
export class ParticipantsComponent implements OnInit {
  data?: ParticipantList;
  error = '';

  constructor(private route: ActivatedRoute, private eventService: EventService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.load(id);
    }
  }

  load(id: number): void {
    this.eventService.participants(id).subscribe({
      next: (data) => (this.data = data),
      error: () => (this.error = 'Nu am putut încărca participanții.'),
    });
  }

  exportCsv(): void {
    if (!this.data) return;
    const rows = [
      ['Nume', 'Email', 'Ora înscrierii'],
      ...this.data.participants.map((p) => [p.full_name || '-', p.email, p.registration_time]),
    ];
    const csv = rows.map((r) => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `participanti-${this.data.event_id}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
}
