Despues de configurar e instalar los paquetes, cada vez que entre hay que activar el entorno ⇒ pipenv shell <br>
Configurar el entorno virutal de django
   ```python
   cd ASW_Hackernews_django
   pip install pipenv
   pipenv --python 3.8
   pip install Django
   pipenv shell
   python manage.py runserver
   ```
Si no quiero usar pipenv, se puede activar el entorno virtual de la siguente manera:
   ```python
   virtualenv env
   . env/bin/activate
   ```
<br>

***
***
# DJANGO SERVER SIDE      
Django en backend soporta varios tipos de BD como PostgreSQL, Oracle, MySQL o SQLite, y hay que especificar la que vamos a usar en `settings.py`, en la parte `DATABASES`. Por defecto, django usa **sqlite** ya que es mas simple, no requiere ninguna instalacion, contiene toda la BD en un SOLO archivo y va bien para proyectos pequeños.

Para restaurar BD (hay que borrar el archivo db.sqlite3 y de la carpeta migrations borrar los archivos excepto __init__)

Estos comandos hay que usar una vez que tengamos la BD
   ```python
   python manage.py makemigrations (genera SQL commands)
   python manage.py migrate (crea la BD sqlite)
   ```
Con esto django construye la BD seguiendo el codigo que esta definido en `models.py` 


## Django Admin
Django proporciona una interfaz de admin para realizar cambios o interactuar con nuestros datos (base de datos). Esta caracteristica no todos los framework proporcionan. 
- para usarlo tenemos que crear un superuser para log in ⇒ `(shell) $ python manage.py createsuperuser` (hay que poner nombre, email y una contraseña)
- python manage.py runserver
- http://127.0.0.1:8000/admin/

```python
[paquetes necesarios]
pip install whitenoise
pip install social-auth-app-django
pip install djangorestframework
pip install django-rest-multiple-models
pip install django-cors-headers
pip install rest-social-auth
pip install django-oauth2-provider
pip install django-oauth-toolkit
pip install django-rest-framework-social-oauth2
pip install drf-yasg
pip install django-polymorphic

# estos paquetes no son necesarios
pip install djangorestframework-api-key
pip install apiview
pip install django-allauth
pip install python-social-auth
```
***
***     
# PARTE 1: Crear app web en server side
## crear scaffolding
```python
(shell) $ django-admin startproject hackernews_project .
    ├── hackernews_project
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
    ├── Pipfile
    └── Pipfile.lock
(shell) $ python manage.py startapp hackernews
    ├── hackernews_project
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── hackernews
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── Pipfile
└── Pipfile.lock
```
- `admin.py` is a configuration file for the built-in Django Admin app
- `apps.py`is a configuration file for the app itself
- `migrations/` keeps track of any changes to our `models.py` file so our database and `models.py` stay in sync
- `models.py` is where we define our database models, which Django automatically
translates into database tables
- `views.py` is where we handle the request/response logic for our web app

hemos creado el proyecto pero Django no sabe donde esta y hay que especificarlo en `settings.py` ('hackernews.apps.HackernewsConfig')

## Django request/response cycle 
URL ⇒ View ⇒ Model (typically) ⇒ Template

cuando hacemos esto con django <a href="{% url 'ask' %}"></a> significa que en la `urls.py` (que controla entry point) tenemos una url definida con el nombre "ask" os objetos request, user, .. son importantes ya que me permite obtener datos para analizar el proceso

en la carpeta templates tenemos los documentos html, esta ruta hay que especificar en `settings.py`

la pagina base.html es importante, hacemos referencia en otras paginas ya que la parte superior y inferior de la pagina se mantiene igual en otras paginas

base.html ⇒ el codigo incorporado podemos reusar en otras plantillas simplemente haciendo `{% extends 'base.html' %}` y para seguir añadiendo contenido en una pagina concreta a parte de usar esta base tendremos que usar 

    {% block content %} # en lugar de content puede title, body, etc
        ....
    {% endblock content %}
Pero cuando queremos cargar un fichero, hay que cargar de esta manera ⇒ {% load hackernews_extra %}

get(), this funcion is like put() o other verbs methods <br>
&nbsp; &nbsp; get_queryset() used by ListViews - it determines the list of objects that you want to display <br>
&nbsp; &nbsp; get_context_data() is used to populate a dictionary to use as the template context, probably be overriding this method most often to add things to display in your templates, like data['itle'] = 'smt'

En todas las clases de vista como TemplateView, ListView (en este hay que especificar el nombre del dato con el que se va a trabajar),... y se ha de especificar el nombre de template <br>
&nbsp; &nbsp; En la clase `models.py`, la clase que quiere definir los campos de la BD tiene que heredar de la clase models.Model ya que facilita la creacion de estos 

Para añadir algunas paginas de estilo, scripts o imagenes en nuestro proyecto va bien agregarlas en una carpeta ("static") y debemos especificar la ruta en `settings.py` en la parte STATICFILES_DIRS <br>
&nbsp; &nbsp; si queremos usar esta carpeta estatica en nuestras plantillas (html) debemos cargarla al inicio del documento con `{% load static %}` y por ejemplo si queremos cargar el css debemos linkar de esta manera: `<link href="{% static 'css/base.css' %}" rel="stylesheet">`

**Forms**: los formularios son comunes en todas las paginas y a veces son dificiles de implementar correctamente. <br>
&nbsp; &nbsp; Cada vez que aceptamos o cogemos los datos introducimos por el usuario tenemos que preocuparnos de la seguridad (XSS Attacks). Con django podemos añadir `{% csrf_token %}` en el formulario que nos proporcionar una buena seguridad a la hora de coger los datos.

**User accounts (user authentication)** <br>
&nbsp; &nbsp; django nos proporciona un User object que tiene sus propiedades como username, password, email, first_name, last_name, etc, con este objeto podremos implementar signup, login, logout, etc; por ejemplo podemos hacer lo siguiente: `{% if user.is_authenticated %}` ... <br>
&nbsp; &nbsp; LOGIN_REDIRECT_URL = 'name url' ⇒ despues de hacer login hace un redirect en el enlace indicado <br>
   <br>
&nbsp; &nbsp; para hacer login con GMAIL usamos el provider del google: <br>
&nbsp; &nbsp; enviamos al usuario al proveider para registrarse pero antes hay que hacer las configuraciones en settings.py ⇒ `<a  href="{% url 'social:begin' 'google-oauth2' %}?next={{ request.path }}">Login by Google</a>`

**"context"** is a dictionary that we can construct in view and send it to html to use it, in another word, context is an object that the template can use it for rendering

Para personalizar los formularios tenemos definidos en forms.py <br>
&nbsp; &nbsp; manejamos formularios con class-based views, para formulario tenemos 3 procesos: initial GET, POST with invalid data & POST with valid data <br>
&nbsp; &nbsp; tenemos una variable form_class = FormClass donde especificamos que formulario vamos a usar

cuando quieres que en un html ejecute otro, pe. hay que indicarlo de esta manera `{% include "comment.html" %}`


# HEROKU      
## configurar heroku
> sudo snap install --classic heroku

>(shell) $ heroku login (heroku email and password)

tenemos que hacer algunos cambios en los siguientes archivos:
  - generar Pipfile.lock ⇒ (shell) $ pipenv lock
  - hacer un archivo nuevo Procfile para heroku ⇒ (shell) $ touch Procfile; dentro escribir ⇒ web: gunicorn hackers_project.wsgi --log-file -
  - instalar gunicorn: (shell) $ pip install gunicorn
  - en `settings.py` añadir: ALLOWED_HOSTS = ['*']

## deploy con heroku (PaaS)
  - crear una app en heroku para poder hacer push en ella ⇒ (shell) $ heroku create ⇒ aqui heroku va proporcionar un nombre aleatorio a nuestra app
  - añadir un git remote para atar heroku ⇒ (shell) $ heroku git:remote -a poner_nombre_generado_por_heroku
  - configurar la app para archivos static ⇒ django no ofrece el manejo de archivos static, por tanto usaremos una libreria WhiteNoise que si que ofrece (esta libreria tendremos que especificarla en `settings.py`) 
  - empezar con el servidor heroku para obtener el host ⇒ (shell) $ git push heroku master
  - a medida que los sitios web crecen en tráfico, necesitan servicios adicionales de Heroku y usaremos el nivel basico ⇒ (shell) $ heroku ps:scale web=ǐ
  (shell) $ heroku open

<br>

***
***

# PARTE 2: CONSTRUIR UNA API REST 
Lenguajes de documentacion del APIs web o Microservicios ⇒ **Swagger/OpenAPI**

## configuracion
activamos shell ⇒ pipenv shell <br>
instalamos django rest framework ⇒ pip install djangorestframework <br>
tenemos el proyecto creado <br>
tambien tenemos creada la app y la BD <br>
&nbsp; &nbsp; dentro de la carpeta api esta el documento en yaml, la vista de api y como tiene que serializar los datos a enviar <br>
configuracion en `settings.py`

Definir los endpoints de API en urls.py de la app <br>
Conectamos urls con las vistas de API <br>
La vista obtiene los datos correspondientes del modelo <br>
Envia los datos a serializar en JSON, los recupera y envia al usuario <br>
   
No nos interesa comprobar el funcionamineto de la API en el navegador, pe: http://127.0.0.1:8000/api/asks , ya que el propio navegador da un formato visual a los contenidos que devuelve la API (en JSON); sino nos conviene hacer las peticiones desde **Postman o swagger editor**

## Ejemplo de algunas funciones importantes:
``` python
   obj = ContributionAsk.objects.filter(id_contribution=id) ⇒ con filter hay que acceder como obj[0].id_contribution
   obj.save()
   obj.update(title=title, text=text)
   obj.delete()

   obj = ContributionAsk.objects.all()
   obj.order_by('-creation_date')

   obj = Contribution.objects.get(id_contribution=form.cleaned_data['parent'])

   form = self.form_class(request.POST)
   goto = form.data['goto']   


   request.user
   request.method
   request.GET.get('id')
   request.POST
   request.META["HTTP_AUTHORIZATION"]
   request.data['about']
   
   para responder:
   render(request, self.template_name, {'form': form})
   Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
   HttpResponse(render(request, self.template_name, {'form': form}))
   HttpResponseRedirect(reverse('home'))
   HttpResponseRedirect(form.cleaned_data['goto'])
   HttpResponseRedirect('/item?id=%s' % (url_existent[0].id_contribution))
```