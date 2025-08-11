import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.inscriptions.models import Inscription


class Command(BaseCommand):
    help = 'Export inscriptions to CSV where transcription field is not empty'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path (default: inscriptions_with_transcription_TIMESTAMP.csv)'
        )

    def handle(self, *args, **options):
        # Generate default filename with timestamp if not provided
        if options['output']:
            output_file = options['output']
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'inscriptions_with_transcription_{timestamp}.csv'

        # Build query to filter inscriptions with non-empty transcription field only
        query = Q(transcription__isnull=False) & ~Q(transcription__exact='')

        # Get inscriptions matching the criteria
        inscriptions = Inscription.objects.filter(query).distinct().prefetch_related(
            'panel', 'type_of_inscription', 'genre', 'tags', 'language', 
            'writing_system', 'dating_criteria', 'mentioned_person', 'inscriber',
            'condition', 'alignment', 'extra_alphabetical_sign', 'bibliography', 'author'
        )

        self.stdout.write(f'Found {inscriptions.count()} inscriptions with transcription data')

        # Define CSV headers
        headers = [
            'id', 'title', 'position_on_surface', 'panel_title', 'panel_room',
            'type_of_inscription', 'genres', 'tags', 'elevation', 'height', 'width',
            'language', 'writing_system', 'min_year', 'max_year', 'dating_criteria',
            'transcription', 'interpretative_edition', 'romanisation',
            'mentioned_persons', 'inscriber', 'translation_eng', 'translation_ukr',
            'comments_eng', 'comments_ukr', 'conditions', 'alignments',
            'extra_alphabetical_signs', 'bibliography_items', 'authors',
            'created_at', 'updated_at'
        ]

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)

            for inscription in inscriptions:
                # Helper function to safely get string representation
                def safe_str(obj):
                    return str(obj) if obj is not None else ''

                # Helper function to join many-to-many relationships
                def join_m2m(queryset, attr='__str__'):
                    if attr == '__str__':
                        return '; '.join([str(obj) for obj in queryset.all()])
                    else:
                        return '; '.join([getattr(obj, attr, '') for obj in queryset.all()])

                # Prepare row data
                row = [
                    inscription.id,
                    safe_str(inscription.title),
                    safe_str(inscription.position_on_surface),
                    safe_str(inscription.panel.title if inscription.panel else ''),
                    safe_str(inscription.panel.room if inscription.panel else ''),
                    safe_str(inscription.type_of_inscription),
                    join_m2m(inscription.genre),
                    join_m2m(inscription.tags),
                    safe_str(inscription.elevation),
                    safe_str(inscription.height),
                    safe_str(inscription.width),
                    safe_str(inscription.language),
                    safe_str(inscription.writing_system),
                    safe_str(inscription.min_year),
                    safe_str(inscription.max_year),
                    join_m2m(inscription.dating_criteria),
                    safe_str(inscription.transcription),
                    safe_str(inscription.interpretative_edition),
                    safe_str(inscription.romanisation),
                    join_m2m(inscription.mentioned_person),
                    safe_str(inscription.inscriber),
                    safe_str(inscription.translation_eng),
                    safe_str(inscription.translation_ukr),
                    safe_str(inscription.comments_eng),
                    safe_str(inscription.comments_ukr),
                    join_m2m(inscription.condition),
                    join_m2m(inscription.alignment),
                    join_m2m(inscription.extra_alphabetical_sign),
                    join_m2m(inscription.bibliography),
                    join_m2m(inscription.author),
                    safe_str(inscription.created_at),
                    safe_str(inscription.updated_at)
                ]

                writer.writerow(row)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {inscriptions.count()} inscriptions to {output_file}'
            )
        )

        # Display file size
        file_size = os.path.getsize(output_file)
        self.stdout.write(f'File size: {file_size:,} bytes')
