import TextAnalyser as TAnalyser
import IgnoreCoordinates

TextAnalyser = TAnalyser.TextAnalyser('/PDFs/ALPHA1.pdf', IgnoreCoordinates.IgnoreCoordinates())

TextAnalyser.segment_pages()
