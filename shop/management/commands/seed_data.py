from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User
from shop.models import Category, Product
from blog.models import Post


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@atelier.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin1234')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin1234)'))

        # Categories
        categories_data = [
            ('Dresses', 'Elegant gowns and dresses for every occasion'),
            ('Accessories', 'Hats, bags, shoes and finery'),
            ('Outerwear', 'Cloaks, coats, and capes'),
            ('Historical', 'Period-accurate garments from various eras'),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'description': desc}
            )
            categories[name] = cat

        # Products
        products_data = [
            ('Midnight Velvet Ball Gown', categories['Dresses'], 78.00,
             'A breathtaking ball gown crafted from deep midnight velvet, '
             'adorned with delicate gold thread embroidery along the bodice. '
             'The full skirt features layers of tulle beneath for a dramatic silhouette. '
             'Perfect for formal occasions and evening gatherings.',
             15, True),
            ('Tudor Rose Day Dress', categories['Dresses'], 55.00,
             'Inspired by Tudor-era fashion, this charming day dress features '
             'a fitted bodice with a square neckline and puffed sleeves. '
             'The skirt is a rich damask-patterned fabric in warm rose tones.',
             20, True),
            ('Enchanted Forest Cloak', categories['Outerwear'], 45.00,
             'A hooded cloak in deep emerald green, lined with champagne silk. '
             'Features an antique brass clasp at the throat and subtle '
             'leaf-pattern embroidery along the hem.',
             12, True),
            ('Pearl-Adorned Tiara', categories['Accessories'], 32.00,
             'A delicate tiara featuring hand-set freshwater pearl beads '
             'and crystal accents on a silver-toned wire frame. '
             'Adjustable to fit various doll head sizes.',
             25, True),
            ('Victorian Mourning Dress', categories['Historical'], 68.00,
             'An exquisitely detailed mourning dress in jet black silk taffeta. '
             'Features a high collar, leg-of-mutton sleeves, and a bustle-back skirt. '
             'Trimmed with black jet beads and crepe.',
             8, False),
            ('Leather Satchel & Belt Set', categories['Accessories'], 28.00,
             'A miniature leather satchel with working buckle closure, '
             'paired with a matching belt. Perfect for adventuring dolls.',
             30, False),
            ('Winter Ermine Capelet', categories['Outerwear'], 52.00,
             'A luxurious short capelet in faux ermine with black tail accents. '
             'Lined in crimson satin with a gold chain closure at the front.',
             10, False),
            ('Regency Empire Gown', categories['Historical'], 62.00,
             'A flowing empire-waist gown in ivory muslin with delicate '
             'sprig embroidery. Short puffed sleeves and a satin sash '
             'beneath the bust. Jane Austen would approve.',
             14, False),
        ]
        for name, category, price, desc, stock, featured in products_data:
            Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    'name': name,
                    'category': category,
                    'price': price,
                    'description': desc,
                    'stock': stock,
                    'is_active': True,
                    'is_featured': featured,
                }
            )

        # Blog Posts
        posts_data = [
            ('The Art of Miniature Tailoring',
             'Every stitch tells a story. In the world of doll couture, precision is paramount — '
             'a single millimetre can make the difference between a garment that drapes beautifully '
             'and one that falls flat.\n\n'
             'Our atelier uses the same techniques employed by master tailors of centuries past: '
             'hand-felled seams, bound buttonholes, and carefully pressed darts. The only difference '
             'is the scale.\n\n'
             'Working at 1:6 scale presents unique challenges. Fabrics must be carefully selected — '
             'too thick, and the garment looks bulky; too thin, and it won\'t hold its shape. '
             'We favour silk organza, fine cotton lawn, and lightweight wool crepe for the most '
             'realistic results.\n\n'
             'Each piece in our collection requires between 8 and 40 hours of meticulous handwork. '
             'From drafting the pattern to the final pressing, every step is performed with the same '
             'care and attention as a full-sized haute couture garment.'),
            ('Behind the Scenes: Creating the Midnight Velvet Ball Gown',
             'The Midnight Velvet Ball Gown has been one of our most requested pieces, and today '
             'we\'re pulling back the curtain on its creation.\n\n'
             'The journey began with a sketch inspired by portraits of Empress Elisabeth of Austria. '
             'Her legendary beauty and style have influenced countless designers, and we wanted to '
             'capture that same sense of regal elegance in miniature.\n\n'
             'The velvet was sourced from a specialty fabric house in Lyon, France — the same city '
             'that has been the heart of European silk production since the Renaissance. The gold '
             'thread embroidery was worked freehand, using a single strand of metallic thread and '
             'a size 12 needle.\n\n'
             'The underskirt consists of five layers of tulle, each cut and hemmed by hand, '
             'creating the voluminous silhouette that gives the gown its dramatic presence.\n\n'
             'We hope you love wearing it as much as we loved creating it.'),
            ('A Guide to Historical Doll Fashion Periods',
             'Understanding historical fashion periods can help you build a truly magnificent '
             'doll wardrobe. Here is a brief guide to the eras that inspire our work.\n\n'
             'MEDIEVAL (500-1500): Think flowing gowns, rich colours, and elaborate headdresses. '
             'Fabrics were often heavy — brocade, damask, and velvet.\n\n'
             'TUDOR (1485-1603): Structured silhouettes, square necklines, and lavish embroidery. '
             'The farthingale gave skirts their distinctive bell shape.\n\n'
             'GEORGIAN (1714-1837): Panniers widened skirts to extraordinary proportions. '
             'Pastel colours, floral patterns, and elaborate wigs defined the era.\n\n'
             'REGENCY (1811-1820): A dramatic shift to high waists and flowing lines. '
             'Light muslins replaced heavy silks, and the silhouette became almost columnar.\n\n'
             'VICTORIAN (1837-1901): Perhaps the most varied era, from the crinolines of the 1850s '
             'to the bustles of the 1880s. Rich colours, heavy fabrics, and intricate trimming.\n\n'
             'Each era offers unique inspiration for doll couture, and we draw from all of them '
             'in our atelier.'),
        ]
        for i, (title, content) in enumerate(posts_data):
            Post.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    'title': title,
                    'content': content,
                    'author': admin,
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded: {Category.objects.count()} categories, '
            f'{Product.objects.count()} products, '
            f'{Post.objects.count()} posts'
        ))
