import TextAnalyser as TAnalyser
import IgnoreCoordinates
import os

TextAnalyser = TAnalyser.TextAnalyser(os.path.join('dataAquisition', 'PDF', 'Grundfosliterature-106.pdf'), IgnoreCoordinates.IgnoreCoordinates())

TextAnalyser.__Test__()
