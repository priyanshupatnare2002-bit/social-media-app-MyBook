from pathlib import Path
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from base.models import Comment, FollowersCount, LikePost, Post, Profile


class Command(BaseCommand):
    help = "Create demo users, profiles, posts, follows, likes, and comments."

    def handle(self, *args, **options):
        User = get_user_model()
        static_root = Path(settings.BASE_DIR) / "static" / "images"
        media_root = Path(settings.MEDIA_ROOT)
        (media_root / "profile_images").mkdir(parents=True, exist_ok=True)
        (media_root / "images").mkdir(parents=True, exist_ok=True)

        people = [
            {
                "username": "maya",
                "fname": "Maya",
                "lname": "Sharma",
                "description": "UX designer sharing clean interfaces, coffee notes, and campus snapshots.",
                "profile": static_root / "home" / "profile-3.jpg",
                "post": static_root / "home" / "feed-1.jpg",
                "title": "Morning design review",
                "caption": "Polished a new profile card layout and it finally feels ready.",
                "location": "Bengaluru",
            },
            {
                "username": "arjun",
                "fname": "Arjun",
                "lname": "Mehta",
                "description": "Full-stack learner building small products and documenting the journey.",
                "profile": static_root / "home" / "profile-7.jpg",
                "post": static_root / "home" / "feed-4.jpg",
                "title": "Weekend hack session",
                "caption": "Added auth, posts, likes, and a nicer suggestion panel today.",
                "location": "Mumbai",
            },
            {
                "username": "zoya",
                "fname": "Zoya",
                "lname": "Khan",
                "description": "Photographer, traveler, and person who notices good light everywhere.",
                "profile": static_root / "home" / "profile-11.jpg",
                "post": static_root / "home" / "feed-6.jpg",
                "title": "City lights",
                "caption": "A small walk turned into my favorite photo set this week.",
                "location": "Delhi",
            },
            {
                "username": "rohan",
                "fname": "Rohan",
                "lname": "Iyer",
                "description": "Data student posting charts, fitness streaks, and project updates.",
                "profile": static_root / "home" / "profile-15.jpg",
                "post": static_root / "posts" / "pie-chart.png",
                "title": "Mini analytics board",
                "caption": "Turned this week's engagement numbers into a simple visual summary.",
                "location": "Pune",
            },
        ]

        profiles = []
        for person in people:
            user, created = User.objects.get_or_create(
                username=person["username"],
                defaults={"email": f"{person['username']}@example.com"},
            )
            if created:
                user.set_password("demo12345")
                user.save()

            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "username": person["username"],
                    "fname": person["fname"],
                    "lname": person["lname"],
                    "description": person["description"],
                },
            )
            profile.username = person["username"]
            profile.fname = person["fname"]
            profile.lname = person["lname"]
            profile.description = person["description"]
            self._attach_file(profile, "profileimg", person["profile"], "profile_images")
            profile.save()
            profiles.append((profile, person))

        for profile, person in profiles:
            post, created = Post.objects.get_or_create(
                author=profile,
                title=person["title"],
                defaults={
                    "title_tag": "Demo",
                    "caption": person["caption"],
                    "location": person["location"],
                    "no_of_likes": 2,
                },
            )
            if created or not post.image:
                self._attach_file(post, "image", person["post"], "images")
                post.save()

            Comment.objects.get_or_create(
                post=post,
                name="Maya",
                body="This makes the feed feel alive.",
            )
            Comment.objects.get_or_create(
                post=post,
                name="Arjun",
                body="Nice update. The profile page looks good too.",
            )
            for liker in ["maya", "arjun"]:
                LikePost.objects.get_or_create(post_id=str(post.id), username=liker)

        for follower, followed in [
            ("maya", "arjun"),
            ("maya", "zoya"),
            ("arjun", "maya"),
            ("zoya", "rohan"),
            ("rohan", "maya"),
        ]:
            FollowersCount.objects.get_or_create(follower=follower, user=followed)

        self.stdout.write(
            self.style.SUCCESS("Demo data ready. Login with maya / demo12345 or arjun / demo12345.")
        )

    def _attach_file(self, instance, field_name, source, subdir):
        if not source.exists():
            return
        destination = Path(settings.MEDIA_ROOT) / subdir / source.name
        if not destination.exists():
            shutil.copyfile(source, destination)
        field = getattr(instance, field_name)
        with destination.open("rb") as image_file:
            field.save(source.name, File(image_file), save=False)
