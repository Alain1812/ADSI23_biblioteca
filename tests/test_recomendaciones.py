import unittest
from unittest.mock import patch
from LibraryController import LibraryController

class TestLibraryController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = LibraryController()

    @patch('library_controller.LibraryController.get_users_who_reserved_book')
    @patch('library_controller.LibraryController.get_book_info')
    def test_recommend_based_on_non_empty_history(self, mock_get_book_info, mock_get_users_who_reserved_book):
        # Datos de prueba simulados
        reservations = [
            {"ID_Reserva": "a1", "ID_Usuario": "james@gmail.com", "ID_Libro": "1", "Fecha_Reserva": "2023-01-01 15:45:30", "Fecha_Vencimiento": "2023-01-01 18:45:30"}
        ]
        mock_get_users_who_reserved_book.return_value = ["james@gmail.com", "jhon@gmail.com"]
        mock_get_book_info.return_value = None  # Ajusta esto según la implementación real de tu método

        number_of_books = 5
        recommended_books = self.controller.recommend_based_on_history(reservations, number_of_books)
        self.assertIsInstance(recommended_books, list)

    @patch('library_controller.LibraryController.select_random_books')
    def test_recommend_based_on_empty_history(self, mock_select_random_books):
        # Simular una lista de reservas vacía
        reservations = []
        mock_select_random_books.return_value = []  # Ajusta esto según la implementación real de tu método

        number_of_books = 5
        recommended_books = self.controller.recommend_based_on_history(reservations, number_of_books)
        mock_select_random_books.assert_called_once_with(number_of_books)
        self.assertIsInstance(recommended_books, list)

if __name__ == '__main__':
    unittest.main()
