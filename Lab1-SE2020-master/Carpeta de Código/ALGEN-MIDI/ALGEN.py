# Creando archivos midi
from midiutil.MidiFile import MIDIFile
# Reproducción de archivos midi
import pygame
import math as Math
import statistics as Stats
import textwrap
from random import randint
from random import uniform
import os
import random

    # CAMPOS CONSTANTES  #
# SE PUEDEN VARIAR PARA CAMBIAR TONOS #
MIDI_TEMPO = 220
INDIVIDUAL_SIZE = 24
PARENT_PERCENT = 0.10
RANDOM_PERCENT = 0.25
MUTANT_PERCENT = 0.55
DEFAULT_MUTATE_NUM = 8
MUTATE_NUM = DEFAULT_MUTATE_NUM
MAX_NOTE_LEN = 4
MIN_NOTE_LEN = .5

def play_midi_file(songfile):
    """
    Función para reproducir un archivo MIDI escrito usando
    pygame
    : param songfile: el nombre del archivo MIDI
    """
    path = "/home/jesusdg/Descargas/Music-Generation/ALGEN-MIDI/Musica_Clasica_Midi/"
    all_mid = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.mid')]

    randomfile = random.choice(all_mid)

    pygame.mixer.init()
    pygame.mixer.music.load(randomfile)
    pygame.mixer.music.play()


def generate_random_individual():
    """
   Función para generar una frase musical aleatoria
    : return: la frase generada aleatoriamente
    """
    new_individual = []

    for beat in range(INDIVIDUAL_SIZE):
        # Genere una nota aleatoria entre (#,#) y duración de nota aleatoria
        new_individual.append([randint(48, 255), beat, uniform(MIN_NOTE_LEN, MAX_NOTE_LEN)])

    return new_individual


def write_midi_file(song, file_name):
    """
   Escriba una frase musical en un archivo MIDI en el mismo directorio.
    Utiliza MIDIUtil.
    : param song: la frase musical para escribir en un archivo
    : param file_name: el nombre del archivo MIDI
    """
    # Crea el objeto MIDIFile con # pista
    my_midi = MIDIFile(12)

    # Las pistas están numeradas desde cero. Los tiempos se miden en latidos. beats.
    track = 4
    time = 4

    # Agrega el nombre y el tempo de la pista.
    my_midi.addTrackName(track, time, "Principal")
    my_midi.addTempo(track, time, MIDI_TEMPO)

    # Agrega una nota. addNote espera la siguiente información:
    track = 8  # (constante)
    channel = 2  # (constante)
    volume = 100  # (constante)

    # Ahora agrega las notas
    for beat in song:
        pitch, time, duration = beat
        my_midi.addNote(track, channel, pitch, time, duration, volume)

    # Y escribe en el disco.
    bin_file = open(file_name, 'wb')
    my_midi.writeFile(bin_file)
    bin_file.close()


def generate_initial_population(size):
    """
    Función para generar la población aleatoria inicial
    : tamaño de parámetro: el tamaño deseado de la población
    : return: la población de frases recién generada
    """
    population = []
    for i in range(size):
        population.append(generate_random_individual())

    return population


def create_next_generation(population, ratings):
    """
    y sus calificaciones individuales
    : población param: la población anterior
    : clasificaciones param: la matriz de clasificaciones de las frases musicales
    : return: la población recién generada
    """
    next_generation = []
    parents = []
    children = []
    mutated = []
    randoms = []
    parent_num = int(Math.floor(len(population)*PARENT_PERCENT))
    random_num = int(Math.floor(len(population)*RANDOM_PERCENT))
    mutant_num = int(Math.floor(len(population)*MUTANT_PERCENT))

    # Obtener los padres
    for i in range(parent_num):
        index_of_max = ratings.index(max(ratings))
        parents.append(population[index_of_max])
        ratings.pop(index_of_max)
        population.pop(index_of_max)

    # Crear los niños
    children.extend(crossover_parents(parents, parent_num))

    # Muta el siguiente mejor de la población anterior
    for i in range(mutant_num):
        index_of_max = ratings.index(max(ratings))
        mutated.append(mutate_individual(population[index_of_max], MUTATE_NUM))
        ratings.pop(index_of_max)
        population.pop(index_of_max)

    # Genera los randoms
    for i in range(random_num):
        randoms.append(generate_random_individual())

    # Agrega cada grupo a la próxima generación
    next_generation.extend(parents)
    next_generation.extend(children)
    next_generation.extend(mutated)
    next_generation.extend(randoms)

    return next_generation


def crossover_parents(parents, child_num):
    """
    Elige a los padres al azar y los cruza para crear
    tantos hijos como especifique child_num.
    Utiliza un cruce de un punto, con el punto elegido al azar.
    : param padres: la matriz de frases principales
    : param child_num: el número de hijos que se generarán
    : return: la matriz de hijos generados
    """
    children = []
    crossover_point = randint(0, INDIVIDUAL_SIZE)

    for i in range(child_num):
        parent_1 = parents[randint(0, len(parents) - 1)]
        parent_2 = parents[randint(0, len(parents) - 1)]

        # Asegurar diferentes padres
        while parent_2 is parent_1:
            parent_2 = parents[randint(0, len(parents) - 1)]

        # Obtiene la primera mitad de un padre
        child = []
        for note in range(crossover_point):
            child.append(parent_1[note])

        # Obtiene la segunda mitad del otro padre
        for note in range(crossover_point, INDIVIDUAL_SIZE):
            child.append(parent_2[note])

        children.append(child)

    return children


def mutate_individual(mutant, num_mutations):
    """
   Mutar una frase musical tantas veces como num_mutations
    especifica.
    Cada mutación elige una nota aleatoria y le da una nueva
    tono y una nueva duración aleatoria.
    : param mutante: la frase musical a ser mutada
    : param num_mutations: el número de mutaciones a realizar
    : return: la frase mutada
    """
    for i in range(num_mutations):
        note_index = randint(0, len(mutant) - 1)
        mutant[note_index] = [randint(48, 84), mutant[note_index][1], uniform(.5, 4)]

    return mutant


def evaluate_individual(individual):
    """
    Evalúa una frase musical utilizando varias características.
    descubrimos que hacen que las notas suenen agradables juntas.
    : param individual: la frase musical a evaluar
    : return: la puntuación otorgada a la frase
    """
    good_diffs = [3, 4, 5, 7, 9]
    neutral_diffs = [0, 2, 6, 8]
    score = 0

    for i in range(len(individual)-1):
        diff_first = individual[0][0] - individual[i][0]
        diff_prev = individual[i][0] - individual[i + 1][0]

        # Compara cada nota con la primera nota
        if diff_first % 12 in good_diffs:
            score += 2
        elif diff_first % 12 in neutral_diffs:
            score += 1
        else:
            score -= 1

        # Compara cada nota con su vecino
        if diff_prev % 12 in good_diffs:
            score += 2
        elif diff_prev % 12 in neutral_diffs:
            score += 1
        else:
            score -= 2

        # Penalizar notas juntas de la otra en diferentes octavas
        if diff_prev > 12:
            score -= 3
        if diff_prev > 8:
            score -= 2

    diff_last = individual[0][0] - individual[INDIVIDUAL_SIZE - 1][0]

    # Compara la primera nota con la última nota
    if diff_last % 12 in good_diffs:
        score += 2
    elif diff_last % 12 in neutral_diffs:
        score += 1
    else:
        score -= 1

    # Penaliza la última nota si es demasiado corta
    if individual[-1][2] < 1.5:
        score -= 3

    return score


def main(size=10, toSave=True, toPlay=True):
    """
    El programa principal.
    Mantiene el algoritmo y escribe el mejor archivo MIDI en
    generación especificada.
    : tamaño de parámetro: el tamaño deseado de la población
    """
    global MUTATE_NUM
    global MUTANT_PERCENT
    global RANDOM_PERCENT
    done = False
    generation = 0
    population = generate_initial_population(size)
    lastMaxRating = 0
    runsStuckAtSameMaxRating = 0
    stabilizeMutation = True

    def printCurrentStats(title='ninguno'):
        ratingsSort = ratings.copy()
        ratingsSort.sort()
        body = textwrap.dedent(f"""
        :{"-" * len(title)}:
        :{title}:
        :{"-" * len(title)}:
            Generacion: {str(generation)}
            Puntuación máxima actual: {str(currentMaxRating)}
            Puntaje más bajo: {str(min(ratings))}
            Media de puntuaciones: {str(Stats.mean(ratings))}
            Calificaciones: {ratingsSort}
            Ejecuciones de puntuación coherentes: {runsStuckAtSameMaxRating}
            Tamaño de la poblacion: {len(population)}
            Fuerza de las mutaciones: {MUTATE_NUM}
            Nueva población aleatoria / mutada: {RANDOM_PERCENT}/{MUTANT_PERCENT}
        """)
        print(body)
    
    while not done:
        ratings = []
        for individual in population:
            ratings.append(evaluate_individual(individual))

        
        if generation % 1000 == 0:
            # print(generation)
            index_of_best = ratings.index(max(ratings))
            best_song = population[index_of_best]
            currentMaxRating = int(ratings[index_of_best])

            # Se ocupa de guardar archivos y restablecer las estadísticas después de un nuevo aumento exitoso.
            if(lastMaxRating < currentMaxRating):
                filename = f"Corrida-Actual/{str(generation)}.mid"
                if toSave:
                    printCurrentStats(f"G U A R D A N D O-- {filename}")
                    write_midi_file(best_song, filename)
                         
                    if input("Deseas buscar una mejor puntuación de melodia? (y/n) \n:") != "y":
                        exit()
                lastMaxRating = currentMaxRating
                runsStuckAtSameMaxRating = 0
                MUTATE_NUM = DEFAULT_MUTATE_NUM                    
                
                if toPlay:
                    print("Reproduciendo " + filename + " con una puntuación de: " + str(ratings[index_of_best]))
                    play_midi_file(filename)

        if generation % 4000 == 0 and generation != 0:
            if runsStuckAtSameMaxRating >= 4000:
                printCurrentStats("chequeando")
            # Ralentiza la cantidad de mutación para ajustar la aleatoriedad
            if stabilizeMutation and MUTATE_NUM > 1:
                MUTATE_NUM -= 1


        # La radiación masiva provoca una mayor probabilidad de mutación si la vida está demasiado estancada.
        if runsStuckAtSameMaxRating >= 20000:

                if runsStuckAtSameMaxRating == 20000:
                    print(f"Nosotros estamos atrapados en: {currentMaxRating}...")
                    print(f"Se inició la fusión del reactor....")
                    stabilizeMutation = False
                    
                if not stabilizeMutation and runsStuckAtSameMaxRating % 4000 == 0 and MUTATE_NUM < INDIVIDUAL_SIZE:
                    MUTATE_NUM += 1
                    print(f"¡Fuga de radiación que causa mutaciones superiores a la media! Número de mutaciones ahora en {str(MUTATE_NUM)}.")
                    if input("Deseas seguir? (y/n) \n:") != "y":
                         exit()
                    
                    if MUTATE_NUM == INDIVIDUAL_SIZE:
                        print("Disminución de la radiación")
                        stabilizeMutation = True

        if runsStuckAtSameMaxRating % 100000 == 0 and runsStuckAtSameMaxRating != 0:
            # Cambia la mutación al más alto
            if(MUTANT_PERCENT != .75):
                MUTANT_PERCENT = .75
                RANDOM_PERCENT = .05

        population = create_next_generation(population, ratings)
        generation += 1
        runsStuckAtSameMaxRating += 1

        
main(size=100, toPlay=False)

           
