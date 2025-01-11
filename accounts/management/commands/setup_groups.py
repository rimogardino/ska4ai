from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

class Command(BaseCommand):
    help = 'Creates moderator group and assigns moderation view permissions'

    def handle(self, *args, **options):
        # Create moderator group
        moderator_group, created = Group.objects.get_or_create(name='Moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Moderators" group'))
        else:
            self.stdout.write(self.style.WARNING('Moderators group already exists'))

        # Create custom permission for moderation view
        content_type = ContentType.objects.get_for_model(Group)  # Using Group as the model since the permission isn't tied to a specific model
        permission, created = Permission.objects.get_or_create(
            codename='can_view_moderation_panel',
            name='Can view moderation panel',
            content_type=content_type,
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created moderation view permission'))
        else:
            self.stdout.write(self.style.WARNING('Moderation view permission already exists'))

        # Add permission to group
        moderator_group.permissions.add(permission)
        self.stdout.write(self.style.SUCCESS('Added permission to Moderators group'))
