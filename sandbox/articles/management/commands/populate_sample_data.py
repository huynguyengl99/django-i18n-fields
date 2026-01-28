"""Management command to populate the database with sample data."""

from django.core.management.base import BaseCommand

from articles.models import Article, Category, Tag


class Command(BaseCommand):
    """Populate the database with sample localized data."""

    help = "Populate the database with sample articles, categories, and tags in multiple languages"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Creating sample data...")

        # Clear existing data
        Article.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        # Create categories
        tech_category = Category.objects.create(
            name={
                "en": "Technology",
                "nl": "Technologie",
                "fr": "Technologie",
                "de": "Technologie",
                "es": "Tecnología",
            },
            description={
                "en": "Articles about technology and innovation",
                "nl": "Artikelen over technologie en innovatie",
                "fr": "Articles sur la technologie et l'innovation",
                "de": "Artikel über Technologie und Innovation",
                "es": "Artículos sobre tecnología e innovación",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created category: {tech_category.name}"))

        science_category = Category.objects.create(
            name={
                "en": "Science",
                "nl": "Wetenschap",
                "fr": "Science",
                "de": "Wissenschaft",
                "es": "Ciencia",
            },
            description={
                "en": "Scientific discoveries and research",
                "nl": "Wetenschappelijke ontdekkingen en onderzoek",
                "fr": "Découvertes scientifiques et recherche",
                "de": "Wissenschaftliche Entdeckungen und Forschung",
                "es": "Descubrimientos científicos e investigación",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created category: {science_category.name}"))

        travel_category = Category.objects.create(
            name={
                "en": "Travel",
                "nl": "Reizen",
                "fr": "Voyage",
                "de": "Reisen",
                "es": "Viajes",
            },
            description={
                "en": "Travel guides and destination reviews",
                "nl": "Reisgidsen en bestemmingsrecensies",
                "fr": "Guides de voyage et avis sur les destinations",
                "de": "Reiseführer und Reiseziel-Bewertungen",
                "es": "Guías de viaje y reseñas de destinos",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created category: {travel_category.name}"))

        # Create tags
        django_tag = Tag.objects.create(
            name={
                "en": "Django",
                "nl": "Django",
                "fr": "Django",
                "de": "Django",
                "es": "Django",
            }
        )

        python_tag = Tag.objects.create(
            name={
                "en": "Python",
                "nl": "Python",
                "fr": "Python",
                "de": "Python",
                "es": "Python",
            }
        )

        web_dev_tag = Tag.objects.create(
            name={
                "en": "Web Development",
                "nl": "Webontwikkeling",
                "fr": "Développement Web",
                "de": "Webentwicklung",
                "es": "Desarrollo Web",
            }
        )

        ai_tag = Tag.objects.create(
            name={
                "en": "Artificial Intelligence",
                "nl": "Kunstmatige Intelligentie",
                "fr": "Intelligence Artificielle",
                "de": "Künstliche Intelligenz",
                "es": "Inteligencia Artificial",
            }
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created {Tag.objects.count()} tags")
        )

        # Create articles
        article1 = Article.objects.create(
            title={
                "en": "Introduction to Django i18n Fields",
                "nl": "Introductie tot Django i18n Fields",
                "fr": "Introduction aux champs i18n Django",
                "de": "Einführung in Django i18n Fields",
                "es": "Introducción a los campos i18n de Django",
            },
            summary={
                "en": "Learn how to build multilingual Django applications with ease",
                "nl": "Leer hoe je eenvoudig meertalige Django-applicaties kunt bouwen",
                "fr": "Apprenez à créer facilement des applications Django multilingues",
                "de": "Erfahren Sie, wie Sie mehrsprachige Django-Anwendungen einfach erstellen",
                "es": "Aprende a crear aplicaciones Django multilingües con facilidad",
            },
            content={
                "en": "Django i18n Fields makes it easy to create multilingual Django applications by providing localized field types that store content in multiple languages using JSON fields. This approach is database-agnostic and works with PostgreSQL, MySQL, and SQLite.",
                "nl": "Django i18n Fields maakt het gemakkelijk om meertalige Django-applicaties te maken door gelokaliseerde veldtypen te bieden die inhoud in meerdere talen opslaan met behulp van JSON-velden. Deze benadering is database-agnostisch en werkt met PostgreSQL, MySQL en SQLite.",
                "fr": "Django i18n Fields facilite la création d'applications Django multilingues en fournissant des types de champs localisés qui stockent le contenu dans plusieurs langues à l'aide de champs JSON. Cette approche est indépendante de la base de données et fonctionne avec PostgreSQL, MySQL et SQLite.",
                "de": "Django i18n Fields erleichtert die Erstellung mehrsprachiger Django-Anwendungen durch Bereitstellung lokalisierter Feldtypen, die Inhalte in mehreren Sprachen mithilfe von JSON-Feldern speichern. Dieser Ansatz ist datenbankunabhängig und funktioniert mit PostgreSQL, MySQL und SQLite.",
                "es": "Django i18n Fields facilita la creación de aplicaciones Django multilingües al proporcionar tipos de campos localizados que almacenan contenido en varios idiomas utilizando campos JSON. Este enfoque es independiente de la base de datos y funciona con PostgreSQL, MySQL y SQLite.",
            },
            view_count={"en": 1250, "nl": 450, "fr": 320, "de": 280, "es": 190},
            rating={"en": 4.8, "nl": 4.7, "fr": 4.9, "de": 4.6, "es": 4.8},
            is_featured={"en": True, "nl": True, "fr": True, "de": False, "es": False},
            category=tech_category,
            published=True,
        )
        article1.tags.add(django_tag, python_tag, web_dev_tag)
        self.stdout.write(self.style.SUCCESS(f"Created article: {article1.title}"))

        article2 = Article.objects.create(
            title={
                "en": "The Future of AI and Machine Learning",
                "nl": "De toekomst van AI en Machine Learning",
                "fr": "L'avenir de l'IA et du Machine Learning",
                "de": "Die Zukunft von KI und Machine Learning",
                "es": "El futuro de la IA y el Machine Learning",
            },
            summary={
                "en": "Exploring the latest trends in artificial intelligence",
                "nl": "Verkenning van de nieuwste trends in kunstmatige intelligentie",
                "fr": "Explorer les dernières tendances en intelligence artificielle",
                "de": "Erkundung der neuesten Trends in der künstlichen Intelligenz",
                "es": "Explorando las últimas tendencias en inteligencia artificial",
            },
            content={
                "en": "Artificial Intelligence and Machine Learning are transforming industries across the globe. From healthcare to finance, AI is revolutionizing how we work and live. This article explores the latest developments and future predictions in the field.",
                "nl": "Kunstmatige Intelligentie en Machine Learning transformeren industrieën over de hele wereld. Van gezondheidszorg tot financiën, AI revolutioneert hoe we werken en leven. Dit artikel verkent de nieuwste ontwikkelingen en toekomstvoorspellingen in het vakgebied.",
                "fr": "L'Intelligence Artificielle et le Machine Learning transforment les industries du monde entier. De la santé à la finance, l'IA révolutionne notre façon de travailler et de vivre. Cet article explore les derniers développements et les prédictions futures dans le domaine.",
                "de": "Künstliche Intelligenz und Machine Learning transformieren Branchen auf der ganzen Welt. Von Gesundheitswesen bis Finanzen revolutioniert KI, wie wir arbeiten und leben. Dieser Artikel untersucht die neuesten Entwicklungen und Zukunftsprognosen im Bereich.",
                "es": "La Inteligencia Artificial y el Machine Learning están transformando industrias en todo el mundo. Desde la atención médica hasta las finanzas, la IA está revolucionando cómo trabajamos y vivimos. Este artículo explora los últimos desarrollos y predicciones futuras en el campo.",
            },
            view_count={"en": 2150, "nl": 680, "fr": 540, "de": 420, "es": 310},
            rating={"en": 4.9, "nl": 4.8, "fr": 5.0, "de": 4.7, "es": 4.9},
            is_featured={"en": True, "nl": False, "fr": True, "de": True, "es": False},
            category=science_category,
            published=True,
        )
        article2.tags.add(ai_tag)
        self.stdout.write(self.style.SUCCESS(f"Created article: {article2.title}"))

        article3 = Article.objects.create(
            title={
                "en": "Top 10 European Destinations for 2025",
                "nl": "Top 10 Europese bestemmingen voor 2025",
                "fr": "Top 10 des destinations européennes pour 2025",
                "de": "Top 10 europäische Reiseziele für 2025",
                "es": "Los 10 mejores destinos europeos para 2025",
            },
            summary={
                "en": "Discover the most amazing places to visit in Europe",
                "nl": "Ontdek de meest geweldige plekken om te bezoeken in Europa",
                "fr": "Découvrez les endroits les plus incroyables à visiter en Europe",
                "de": "Entdecken Sie die erstaunlichsten Orte in Europa zu besuchen",
                "es": "Descubre los lugares más increíbles para visitar en Europa",
            },
            content={
                "en": "Europe offers countless breathtaking destinations for travelers. From the romantic streets of Paris to the historic ruins of Rome, each city has its unique charm. This guide highlights the top 10 must-visit European destinations for 2025.",
                "nl": "Europa biedt talloze adembenemende bestemmingen voor reizigers. Van de romantische straten van Parijs tot de historische ruïnes van Rome, elke stad heeft zijn unieke charme. Deze gids belicht de top 10 must-visit Europese bestemmingen voor 2025.",
                "fr": "L'Europe offre d'innombrables destinations à couper le souffle pour les voyageurs. Des rues romantiques de Paris aux ruines historiques de Rome, chaque ville a son charme unique. Ce guide met en lumière les 10 destinations européennes incontournables pour 2025.",
                "de": "Europa bietet unzählige atemberaubende Reiseziele für Reisende. Von den romantischen Straßen von Paris bis zu den historischen Ruinen von Rom hat jede Stadt ihren einzigartigen Charme. Dieser Leitfaden hebt die Top 10 Must-Visit-Europäischen Reiseziele für 2025 hervor.",
                "es": "Europa ofrece innumerables destinos impresionantes para los viajeros. Desde las románticas calles de París hasta las ruinas históricas de Roma, cada ciudad tiene su encanto único. Esta guía destaca los 10 destinos europeos imprescindibles para 2025.",
            },
            view_count={"en": 3420, "nl": 890, "fr": 1120, "de": 760, "es": 540},
            rating={"en": 4.7, "nl": 4.6, "fr": 4.8, "de": 4.5, "es": 4.7},
            is_featured={"en": False, "nl": True, "fr": False, "de": False, "es": True},
            category=travel_category,
            published=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Created article: {article3.title}"))

        # Create one draft article
        article4 = Article.objects.create(
            title={
                "en": "Draft: Building RESTful APIs with Django",
                "nl": "Concept: RESTful API's bouwen met Django",
                "fr": "Brouillon: Créer des API RESTful avec Django",
                "de": "Entwurf: RESTful APIs mit Django erstellen",
                "es": "Borrador: Construyendo APIs RESTful con Django",
            },
            summary={
                "en": "A comprehensive guide to Django REST Framework",
                "nl": "Een uitgebreide gids voor Django REST Framework",
                "fr": "Un guide complet de Django REST Framework",
                "de": "Ein umfassender Leitfaden für Django REST Framework",
                "es": "Una guía completa de Django REST Framework",
            },
            content={
                "en": "This article is still being written...",
                "nl": "Dit artikel wordt nog geschreven...",
                "fr": "Cet article est encore en cours de rédaction...",
                "de": "Dieser Artikel wird noch geschrieben...",
                "es": "Este artículo aún está siendo escrito...",
            },
            category=tech_category,
            published=False,
        )
        article4.tags.add(django_tag, python_tag)
        self.stdout.write(self.style.SUCCESS(f"Created draft article: {article4.title}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Sample data created successfully!\n"
                f"  - {Category.objects.count()} categories\n"
                f"  - {Tag.objects.count()} tags\n"
                f"  - {Article.objects.count()} articles ({Article.objects.filter(published=True).count()} published)\n"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "\nYou can now test the API at http://localhost:8000/api/"
            )
        )
