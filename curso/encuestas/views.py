from .models import Pregunta, Opcion

from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.db.models import F
from django.core.urlresolvers import reverse
from django.views import generic

class VistaIndex(generic.ListView):
    template_name = 'encuestas/index.html'
    context_object_name = 'preguntas_recientes'

    def get_queryset(self):
        return Pregunta.objects.order_by('-fe_publicacion')[:5]

    def get_context_data(self, **kwargs):
        context = super(VistaIndex, self).get_context_data(**kwargs)
        context['titulo'] = 'Listado de Encuestas'
        return context

class VistaDetalle(generic.DetailView):
    model = Pregunta
    template_name = 'encuestas/detalle.html'

def votar(request, id_pregunta):
    pregunta = get_object_or_404( Pregunta, pk=id_pregunta )
    try:
        # Nos aseguramos de que el código de la opción recibida esté dentro de las
        # opciones registradas para la pregunta
        opcion_seleccionada = pregunta.opcion_set.get(pk=request.POST['opcion'])

        # Incrementamos la cantidad de votos para la opción seleccionada, pero desde la
        # base de datos directamente
        # opcion_seleccionada.votos += 1 # Esto puede generar problemas en transacciones
                                         # concurrentes
        opcion_seleccionada.votos = F('votos') + 1
        opcion_seleccionada.save()
        # Nota: Lo anterior también podría escribirse de forma compacta como:
        # opcion_seleccionada.update( votos = F('votos') + 1 )

        # Luego de guardar exitosamente, redireccionamos a página de resultados.
        # Utilizamos 'reverse' para obtener de manera reutilizable la URL de la vista a
        # la que queremos redirigir al usuario.
        return HttpResponseRedirect(reverse('encuestas:resultados',
                                            kwargs={'pk': pregunta.id}))
    except (KeyError, Opcion.DoesNotExist):
        # En caso de un código incorrecto o faltante de opción, volver a mostrar el formulario
        return render(request, 'encuestas/detalle.html', {
            'pregunta': pregunta,
            'mensaje_error': "Opción faltante o inválida",
        })

class VistaResultados(generic.DetailView):
    model = Pregunta
    template_name = 'encuestas/resultados.html'
