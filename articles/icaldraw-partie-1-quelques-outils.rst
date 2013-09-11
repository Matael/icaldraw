=====================================
IcalDraw (Partie 1) : Quelques outils
=====================================
-------------------------------------------------------------------
Redessiner un emploi du temps avec Python :: ical, python, svg, fac
-------------------------------------------------------------------

Il y a quelques jours, je me suis rendu compte que l'emploi du temps de cette année serait un peu complexe.
Par "un peu complexe", j'entends qu'entre la connexion à l'ENT et l'affichage de l'emploi du temps correct s'étend un
concert de clics pour sélectionnner les bons groupes, les bonnes options et tout le reste. Pour moi qui suis allergique à la
souris, ça ne pouvait pas le faire....

On va donc essayer de partir de l'API d'export d'emploi du temps (comme dans `cet article`_) pour aboutir à une image
SVG dépouillée de l'inutile avec juste les cours de notés dessus sous forme de lignes temporelles.

Un exemple pour mieux comprendre :

.. image:: /static/images/icaldraw/exemple.png
    :width: 800px
    :align: center

Dans l'ordre, voilà les étapes :

- créer quelques outils pour rendre le script final plus simple :

  - un moyen de récupérer facilement les événements Ical depuis une URL/un fichier
  - un moyen de créer des fichiers SVG et d'y ajouter des éléments [#]_

- écrire le programme lui même permettant la génération des images
- écrire un script l'utilisant

Récupération des évenements Ical
================================

Rien de nouveau ici (tout a été traité dans `cet article`_).

On va se contenter d'écrire un *wrapper* agréable à utiliser pour simplifier le code final.

On reprend donc le code désormais connu pour en faire un module. Les commentaires devraient suffir à sa compréhension.
Pour quelque chose de plus détaillé, reportez vous à l'article sus-cité.

.. sourcecode:: python

    from icalendar import Calendar
    from collections import namedtuple
    from urllib import urlopen

    # Structure de donnée pour les évènements
    Vevent = namedtuple('Vevent', ['dtstart', 'dtend', 'summary', 'location'])

    class IcalFetcher:
        """
        Fetcher for Ical data.
        Provides a wrapper to get clean, sorted list of events

        """

        def __init__(self):

            # init. all to None, this way we can infer which source to use
            # if user doesn't specify it
            self.filename = None
            self.url = None
            self.mode = None

        def from_url(self, url):
            """ Add URL source and change mode to URL """

            self.mode = "URL"
            self.url = url

        def from_file(self, filename):
            """ Add file source and change mode to FILE """

            self.mode = "FILE"
            self.filename = filename

        def __iter__(self):
            """ Add __iter__ special method so we can iterate directly over the object """

            for ev in self.events:
                yield ev


        def get_events(self, mode=None):
            """ Grab list of events and sort them. Source is selected through mode """

            # find which source to use (if no mode's specified on call, use self.mode)
            if mode==None: mode = self.mode

            if mode == "FILE" and self.filename!=None:
                # read data from file
                with open(self.filename, 'r') as f:
                    gcal = Calendar.from_ical(f.read())
            elif mode == "URL" and self.url!=None:
                # open url and read data from it
                gcal = Calendar.from_ical(urlopen(self.url).read())
            else:
                # if mode's unknown, just raise an Exception
                raise ValueError("Supplied mode is not correct. Accepted modes are : FILE, URL")

            # clean and sort events
            events = []
            for component in gcal.walk():
                if component.name == "VEVENT":
                    e = Vevent(dtstart=component.get('dtstart').dt,
                               dtend=component.get('dtend').dt,
                               summary=component.get('summary').encode('utf8'),
                               location=component.get('location').encode('utf8')
                              )
                    events.append(e)
            events.sort(key = lambda ev: ev.dtstart)
            self.events =  events

Nous avons désormais un outil *iterable* qui contiendra les événements triés.

Naissance d'un SVG
==================

Rappel sur le format
--------------------

SVG est un format dérivé du XML.

Il comprend donc une entête suivie de balise indiquant les éléments à afficher et les données s'y rapportant :
coordonnées, contenu, style, etc...

On peut ajouter des élément de style soit via une feuille CSS liée, soit directement par l'attribut ``style`` des balises
XML (ce que nous ferons ici).

Finalement, le tout est placer dans un fichier ``.svg`` qui est en fait un fichier texte bête et méchant.

Une chose à savoir, SVG ne supporte pas les <, > et autres & en dehors des balises, le fichier est alors considéré
incorect et rien ne s'affiche.

Code
----

Il existe des modules pour faire du SVG en Python, mais pour l'utilisation que l'on va en faire, autant en refaire un
qui soit taillé parfaitement pour le boulot.

On va avoir besoin d'ajouter quelques éléments de base :

- des lignes
- des cercles
- du texte
- des rectangles [#]_

C'est parti, la classe s'appellera ``SVGwriter`` (quelle surprise) :

.. sourcecode:: python

    class SVGwriter:


        def __init__(self, w, h, title="", desc=""):
            """
            We do not remember title and desc 'cause we won't need them anymore after header

            """
            self.width = w
            self.height = h

            # output buffer
            self.lines = []

            self._out([
                '<?xml version="1.0" encoding="utf-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">'.format(w, h),
                '<title>{0}</title>'.format(title),
                '<desc>{0}</desc>'.format(desc)
            ])

On va aussi ajouter à la classe un point de sortie. Plutot qu'écrire directement dans le fichier, on va coller les ligne
en tampon les unes après les autres puis la méthode ``save()`` les écrira vraiment.
La méthode ``_out()`` est une méthode privée qui sert de point de sortie.

.. sourcecode:: python

    def _out(self, l):
        """ Append a line or a list of lines to the output buffer """

        if type(l) == list:
            for i in l: self._out(i)
        else:
            self.lines.append(l)

    def save(self, filename):
        """ Save self.lines to filename """

        self._out("</svg>")
        with open(filename, "w") as f:
            for l in self.lines:
                f.write(l)
                f.write('\n')

Ajoutons maintenant les éléments de base.

Rectangle
---------

La recette ressemble à ça ::

    <rect width="LARGEUR" height="HAUTEUR" x="ABSCISSE ORIGINE" y="ORDONNEE ORIGINE" [style="STYLE"] />

.. sourcecode:: python

    def add_rect(self, w, h, x, y, style=""):
        """ Rectangle """

        if style == "":
            self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" />'.format(w, h, x, y))
        else:
            self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" style="{4}" />'.format(w, h, x, y, style))

Et ce sera semblable pour les 3 autres

Cercle
------

On veut ce genre de sortie ::

    <circle cx="ABSCISSE CENTRE" cy="ORDONNEE CENTRE" r="RAYON" [style="STYLE"] />


.. sourcecode:: python

    def add_circle(self, x, y, r, style=""):
        """ Circle """

        if style == "":
            self._out('<circle cx="{0}" cy="{1}" r="{2}" />'.format(x, y, r))
        else:
            self._out('<circle cx="{0}" cy="{1}" r="{2}" style="{3}" />'.format(x, y, r, style))

Ligne
-----

Cette fois, on veut ça ::

    <line x1="ABSCISSE DEBUT" y1="ORDONNEE DEBUT" x2="ABSCISSE FIN" y2="ORDONNEE FIN" [style="STYLE"] />

.. sourcecode:: python

    def add_line(self, x1, y1, x2, y2, style=""):
        """ Line """

        if style == "":
            self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" />'.format(x1, y1, x2, y2))
        else:
            self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="{4}" />'.format(x1, y1, x2, y2, style))

Texte
-----

Enfin, il nous faut ça ::

    <text x="ABSCISSE" y="ORDONNEE" [style="STYLE"]>TEXTE</text>

Attention, le texte doit être nettoyé, d'où le ``replace()`` :

.. sourcecode:: python

    def add_text(self, text, x, y, style=""):
        """ Text """

        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        if style == "":
            self._out('<text x="{0}" y="{1}">{2}</text>'.format(x, y, text))

        else:
            self._out('<text x="{0}" y="{1}" style="{2}">{3}</text>'.format(x, y, style, text))

Et voilà le module complet :

.. sourcecode:: python

    class SVGwriter:


        def __init__(self, w, h, title="", desc=""):
            """
            We do not remember title and desc 'cause we won't need them anymore after header

            """
            self.width = w
            self.height = h

            # output buffer
            self.lines = []

            self._out([
                '<?xml version="1.0" encoding="utf-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">'.format(w, h),
                '<title>{0}</title>'.format(title),
                '<desc>{0}</desc>'.format(desc)
            ])

        def _out(self, l):
            """ Append a line or a list of lines to the output buffer """

            if type(l) == list:
                for i in l: self._out(i)
            else:
                self.lines.append(l)

        def save(self, filename):
            """ Save self.lines to filename """

            self._out("</svg>")
            with open(filename, "w") as f:
                for l in self.lines:
                    f.write(l)
                    f.write('\n')

        def add_rect(self, w, h, x, y, style=""):
            """ Rectangle """

            if style == "":
                self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" />'.format(w, h, x, y))
            else:
                self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" style="{4}" />'.format(w, h, x, y, style))

        def add_circle(self, x, y, r, style=""):
            """ Circle """

            if style == "":
                self._out('<circle cx="{0}" cy="{1}" r="{2}" />'.format(x, y, r))
            else:
                self._out('<circle cx="{0}" cy="{1}" r="{2}" style="{3}" />'.format(x, y, r, style))

        def add_line(self, x1, y1, x2, y2, style=""):
            """ Line """

            if style == "":
                self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" />'.format(x1, y1, x2, y2))
            else:
                self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="{4}" />'.format(x1, y1, x2, y2, style))

        def add_text(self, text, x, y, style=""):
            """ Text """

            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            if style == "":
                self._out('<text x="{0}" y="{1}">{2}</text>'.format(x, y, text))

            else:
                self._out('<text x="{0}" y="{1}" style="{2}">{3}</text>'.format(x, y, style, text))

Conclusion
==========

Nous avons donc nos deux outils, reste à écrire le programe final. La suite au `prochain épisode`_ !

.. [#] Pour la partie SVG, l'ouvrage *SVG Essentials* d'O'Reilly est un vrai plus (ISBN-13 : 978-0596002237 ou `en ligne`_).
.. [#] En bonus, on ne s'en servira pas ici, mais comme ça le module sera un peu plus général... pour 3
  lignes de code en plus :
.. _cet article: /writing/passer-de-lical-au-pdf-un-petit-script/
.. _en ligne: http://commons.oreilly.com/wiki/index.php/SVG_Essentials
.. _prochain épisode: /writing/icaldraw-partie-2-dessine-moi-un-planning/
