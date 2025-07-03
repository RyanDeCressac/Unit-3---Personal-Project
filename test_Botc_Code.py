import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock
import pandas as pd
import hashlib
from Botc_Code import validate_register
from Botc_Code import validate_input
from Botc_Code import findCharacterType
from Botc_Code import checkLogin
from Botc_Code import checkUsername
from Botc_Code import get_total_games
from Botc_Code import get_win_stats
from Botc_Code import get_starting_alignment_stats
from Botc_Code import get_change_stats
from Botc_Code import get_character_stats
from Botc_Code import get_starting_character_stats
from Botc_Code import get_script_stats
from Botc_Code import get_death_stats
from Botc_Code import get_character_counts
from Botc_Code import fetchData

global Connection
global cursor
Connection = MagicMock()
cursor = Connection.cursor()

# Unit Test of validate_register
class TestValidateRegister(unittest.TestCase):
    '''
    Unit testing validate_register() function
    '''
    def test_valid_input(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertTrue(validate_register("ValidUser", "strongpass",cursor))

    def test_empty_username(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("", "password123",cursor))

    def test_empty_password(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "",cursor))

    def test_username_too_long(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("ThisUsernameIsWayTooLong", "password123",cursor))

    def test_username_invalid_characters(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Invalid!Name", "password123",cursor))

    def test_username_not_alphanumeric(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("User123!", "password123",cursor))

    def test_password_too_short(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "pass",cursor))

    def test_password_with_angle_brackets(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "pass<word",cursor))

    def test_password_with_space(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "my pass",cursor))

    def test_username_already_exists(self):
        with patch('Botc_Code.checkUsername', return_value=True):
            self.assertFalse(validate_register("ExistingUser", "securePass",cursor))

    def test_non_string_username(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register(12345, "password123",cursor))

    def test_non_string_password(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", 987654321,cursor))

#Unit Test of validate_input - also tests integration of findCharacterType
class TestValidateInput(unittest.TestCase):
    def test_valid_input(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertTrue(result)

    def test_missing_username(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 10, 1, "")
        self.assertFalse(result)

    def test_missing_required_input(self):
        result = validate_input("", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_character(self):
        result = validate_input("Unknown", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_character_change(self):
        result = validate_input("Sage", "Maybe", "Monk", "Good", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_starting_character(self):
        result = validate_input("Sage", "True", "Sage", "Good", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_alignment(self):
        result = validate_input("Sage", "True", "Monk", "Neutral", "False", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_alignment_change(self):
        result = validate_input("Sage", "True", "Monk", "Good", "Invalid", "True", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_win_input(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "Invalid", "False", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_death_input(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "Invalid", "None", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_death_type(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "Morning", "tb", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_script_input(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "None", "Invalid", 10, 1, "TestUsername")
        self.assertFalse(result)

    def test_invalid_player_count(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 3, 1, "TestUsername")
        self.assertFalse(result)

    def test_negative_traveller_count(self):
        result = validate_input("Sage", "True", "Monk", "Good", "False", "True", "False", "None", "tb", 10, -1, "TestUsername")
        self.assertFalse(result)

#Unit test of findCharacterType
class TestFindCharacterType(unittest.TestCase):
    def test_type_found_townsfolk(self):
        result = findCharacterType("Monk")
        self.assertEqual(result,"Townsfolk")

    def test_type_found_outsider(self):
        result = findCharacterType("Recluse")
        self.assertEqual(result,"Outsider")
    
    def test_type_found_minion(self):
        result = findCharacterType("Baron")
        self.assertEqual(result,"Minion")
    
    def test_type_found_demon(self):
        result = findCharacterType("Imp")
        self.assertEqual(result,"Demon")
    
    def test_type_found_traveller(self):
        result = findCharacterType("Barista")
        self.assertEqual(result,"Traveller")
    
    def test_type_found_no_match(self):
        result = findCharacterType("ThisDoesntExist")
        self.assertEqual(result,None)

#Unit Test of checkLogin
class TestCheckLogin(unittest.TestCase):
    def test_valid_credentials(self):
        # Mock data as if it were returned from the database
        cursor.fetchall.return_value = [("alice", hashlib.sha256("secret".encode()).hexdigest()), ("bob", hashlib.sha256("password".encode()).hexdigest())]
        result = checkLogin("alice", "secret",cursor)
        self.assertTrue(result)

    def test_invalid_username(self):
        cursor.fetchall.return_value = [("alice", hashlib.sha256("secret".encode()).hexdigest()), ("bob", hashlib.sha256("password".encode()).hexdigest())]
        result = checkLogin("charlie", "secret",cursor)
        self.assertFalse(result)

    def test_invalid_password(self):
        cursor.fetchall.return_value = ("alice", hashlib.sha256("secret".encode()).hexdigest())
        result = checkLogin("alice", "wrongpass",cursor)
        self.assertFalse(result)

    def test_empty_database(self):
        cursor.fetchall.return_value = []
        result = checkLogin("anyone", "password",cursor)
        self.assertFalse(result)

#Unit Test of checkUsername
class TestCheckUsername(unittest.TestCase):
    def test_username_exists(self):
        cursor = Mock()
        cursor.fetchall.return_value = [('alice',), ('bob',)]
        result = checkUsername('alice', cursor)
        self.assertTrue(result)

    def test_username_does_not_exist(self):
        cursor = Mock()
        cursor.fetchall.return_value = [('alice',), ('bob',)]
        result = checkUsername('charlie', cursor)
        self.assertFalse(result)

### START OF TESTING OF THE *WALL OF STAT CALCULATION* FUNCTIONS ###

#Unit test of get_total_games
class TestGetTotalGames(unittest.TestCase):
    def test_all_good(self):
        df = pd.DataFrame({'alignment': ['Good', 'Good', 'Good']})
        result = get_total_games(df)
        self.assertEqual(result, (3, 3, 0))

    def test_all_evil(self):
        df = pd.DataFrame({'alignment': ['Evil', 'Evil']})
        result = get_total_games(df)
        self.assertEqual(result, (2, 0, 2))

    def test_mixed(self):
        df = pd.DataFrame({'alignment': ['Good', 'Evil', 'Good', 'Evil']})
        result = get_total_games(df)
        self.assertEqual(result, (4, 2, 2))

    def test_empty(self):
        df = pd.DataFrame({'alignment': []})
        result = get_total_games(df)
        self.assertEqual(result, (0, 0, 0))

#Unit test of get_win_stats
class TestGetWinStats(unittest.TestCase):
    def test_all_good_win(self):
        df = pd.DataFrame({
            'alignment': ['Good', 'Good'],
            'win': ['True', 'True']
        })
        totalGames = 2
        totalEvilGames = 0
        result = get_win_stats(df, totalGames, totalEvilGames)
        self.assertEqual(result, (2, 2, 0, 2, 0))

    def test_all_evil_win(self):
        df = pd.DataFrame({
            'alignment': ['Evil', 'Evil'],
            'win': ['True', 'True']
        })
        totalGames = 2
        totalEvilGames = 2
        result = get_win_stats(df, totalGames, totalEvilGames)
        self.assertEqual(result, (2, 0, 2, 0, 2))

    def test_mixed(self):
        df = pd.DataFrame({
            'alignment': ['Good', 'Good', 'Evil', 'Evil'],
            'win': ['True', 'False', 'True', 'False']
        })
        totalGames = 4
        totalEvilGames = 2
        result = get_win_stats(df, totalGames, totalEvilGames)
        self.assertEqual(result, (2, 1, 1, 2, 2))

    def test_empty_df(self):
        df = pd.DataFrame({'alignment': [], 'win': []})
        totalGames = 0
        totalEvilGames = 0
        result = get_win_stats(df, totalGames, totalEvilGames)
        self.assertEqual(result, (0, 0, 0, 0, 0))

#Unit test of get_starting_alignment_stats
class TestGetStartingAlignment(unittest.TestCase):
    def test_all_starting_good(self):
        df = pd.DataFrame({
            'alignment': ['Good', 'Evil'],
            'alignment_change': ['False', 'True']
        })
        totalGames = 2
        result = get_starting_alignment_stats(df, totalGames)
        self.assertEqual(result, (2, 0))  # Both qualify as starting good

    def test_all_starting_evil(self):
        df = pd.DataFrame({
            'alignment': ['Evil', 'Good'],
            'alignment_change': ['False', 'True']
        })
        totalGames = 2
        result = get_starting_alignment_stats(df, totalGames)
        self.assertEqual(result, (0, 2))  # Neither qualifies as starting good

    def test_mixed(self):
        df = pd.DataFrame({
            'alignment': ['Good', 'Good', 'Evil', 'Evil'],
            'alignment_change': ['False', 'True', 'True', 'False']
        })
        totalGames = 4
        result = get_starting_alignment_stats(df, totalGames)
        self.assertEqual(result, (2, 2))

    def test_empty_df(self):
        df = pd.DataFrame({'alignment': [], 'alignment_change': []})
        totalGames = 0
        result = get_starting_alignment_stats(df, totalGames)
        self.assertEqual(result, (0, 0))

#Unit test of get_change_stats
class TestGetChangeStats(unittest.TestCase):
    def test_all_no_change(self):
        df = pd.DataFrame({
            'alignment_change': ['False', 'False'],
            'character_change': ['False', 'False']
        })
        result = get_change_stats(df)
        self.assertEqual(result, (2, 0, 0, 0))

    def test_all_character_change_only(self):
        df = pd.DataFrame({
            'alignment_change': ['False', 'False'],
            'character_change': ['True', 'True']
        })
        result = get_change_stats(df)
        self.assertEqual(result, (0, 2, 0, 0))

    def test_all_alignment_change_only(self):
        df = pd.DataFrame({
            'alignment_change': ['True', 'True'],
            'character_change': ['False', 'False']
        })
        result = get_change_stats(df)
        self.assertEqual(result, (0, 0, 2, 0))

    def test_all_change(self):
        df = pd.DataFrame({
            'alignment_change': ['True', 'True'],
            'character_change': ['True', 'True']
        })
        result = get_change_stats(df)
        self.assertEqual(result, (0, 0, 0, 2))

    def test_mixed_cases(self):
        df = pd.DataFrame({
            'alignment_change': ['False', 'False', 'True', 'True'],
            'character_change': ['False', 'True', 'False', 'True']
        })
        result = get_change_stats(df)
        self.assertEqual(result, (1, 1, 1, 1))
    
    def test_empty_df(self):
        df = pd.DataFrame({'alignment_change': [], 'character_change': []})
        result = get_change_stats(df)
        self.assertEqual(result, (0, 0, 0, 0))

#Unit test of get_character_stats - also tests integration of findCharacterType
class TestGetCharacterStats(unittest.TestCase):
    def test_character_stats(self):
        characters = ['Sage', 'Hermit', 'Widow', 'Ojo', 'Harlot']
        wins = ['True', 'False', 'True', 'False', 'True']
        df = pd.DataFrame({
            'character': characters,
            'win': wins
        })
        result = get_character_stats(df)
        self.assertEqual(result, (1, 1, 1, 1, 1, 1, 0, 1, 0, 1))

    def test_empty_df(self):
        df = pd.DataFrame({'character': [], 'win': []})
        result = get_character_stats(df)
        self.assertEqual(result, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

#Unit test of get_starting_character_stats - also tests integration of findCharacterType
class TestGetStartingCharacterStats(unittest.TestCase):
    def test_starting_character(self):
        df = pd.DataFrame({'starting_character': ['Washerwoman', 'Butler', 'Spy', 'Imp', 'Beggar']})
        result = get_starting_character_stats(df)
        self.assertEqual(result, (1, 1, 1, 1, 1))
    
    def test_empty_dataframe(self):
        df = pd.DataFrame({'starting_character': []})
        result = get_starting_character_stats(df)
        self.assertEqual(result, (0, 0, 0, 0, 0))

    def test_multiple_of_same_type(self):
        df = pd.DataFrame({'starting_character': ['Scarlet Woman', 'Poisoner', 'Baron']})
        result = get_starting_character_stats(df)
        self.assertEqual(result, (0, 0, 3, 0, 0))

#Unit test of get_script_stats
class TestGetScriptStats(unittest.TestCase):
    def test_all_types_and_wins(self):
        df = pd.DataFrame({
            'script_type': ['tb', 'tb', 'bmr', 'snv', 'custom', 'custom', 'bmr', 'snv'],
            'win': ['True', 'False', 'True', 'True', 'False', 'True', 'False', 'False']
        })
        result = get_script_stats(df)
        self.assertEqual(result, (2, 2, 2, 2, 1, 1, 1, 1))

    def test_empty_dataframe(self):
        df = pd.DataFrame({'script_type': [], 'win': []})
        result = get_script_stats(df)
        self.assertEqual(result, (0, 0, 0, 0, 0, 0, 0, 0))

    def test_single_script_only(self):
        df = pd.DataFrame({
            'script_type': ['tb', 'tb', 'tb'],
            'win': ['True', 'False', 'True']
        })
        result = get_script_stats(df)
        self.assertEqual(result, (3, 0, 0, 0, 2, 0, 0, 0))

#Unit test of get_death_stats
class TestGetDeathStats(unittest.TestCase):
    def test_mixed_deaths_and_wins(self):
        df = pd.DataFrame({
            'death': ['True', 'False', 'True', 'False'],
            'death_type': ['Day', 'Night', 'Night', 'Day'],
            'win': ['True', 'True', 'False', 'True']
        })
        totalGames = 4
        totalWins = 3
        result = get_death_stats(df, totalGames, totalWins)
        self.assertEqual(result, (2, 2, 2, 2, 1, 2))

    def test_all_alive(self):
        df = pd.DataFrame({
            'death': ['False', 'False'],
            'death_type': ['Day', 'Night'],
            'win': ['True', 'False']
        })
        totalGames = 2
        totalWins = 1
        result = get_death_stats(df, totalGames, totalWins)
        self.assertEqual(result, (0, 2, 1, 1, 0, 1))

    def test_all_dead(self):
        df = pd.DataFrame({
            'death': ['True', 'True'],
            'death_type': ['Day', 'Day'],
            'win': ['False', 'True']
        })
        totalGames = 2
        totalWins = 1
        result = get_death_stats(df, totalGames, totalWins)
        self.assertEqual(result, (2, 0, 2, 0, 1, 0))

    def test_empty_df(self):
        df = pd.DataFrame({'death': [], 'death_type': [], 'win': []})
        result = get_death_stats(df, totalGames=0, totalWins=0)
        self.assertEqual(result, (0, 0, 0, 0, 0, 0))

#Unit test of get_character_counts
class TestGetCharacterCounts(unittest.TestCase):
    def test_basic_counts(self):
        df = pd.DataFrame({
            'character': ['A', 'B', 'A', 'C', 'B', 'B'],
            'starting_character': ['A', 'A', 'B', 'C', 'C', 'C']
        })

        character_counts, starting_counts = get_character_counts(df)

        expected_char_counts = pd.Series({'B': 3, 'A': 2, 'C': 1})
        expected_start_counts = pd.Series({'C': 3, 'A': 2, 'B': 1})

        pd.testing.assert_series_equal(character_counts, expected_char_counts, check_names=False)
        pd.testing.assert_series_equal(starting_counts, expected_start_counts, check_names=False)

    def test_empty_dataframe(self):
        df = pd.DataFrame({'character': [], 'starting_character': []})
        character_counts, starting_counts = get_character_counts(df)

        self.assertTrue(character_counts.empty)
        self.assertTrue(starting_counts.empty)

#Integration test of Fetch Data
class TestFetchDataIntegration(unittest.TestCase):
    def test_fetch_data(self):
        df = pd.DataFrame({
        'alignment': ['Good', 'Evil', 'Good', 'Evil'],
        'win': ['True', 'False', 'True', 'True'],
        'alignment_change': ['False', 'True', 'False', 'True'],
        'character_change': ['True', 'False', 'False', 'True'],
        'character': ['Washerwoman', 'Recluse', 'Poisoner', 'Imp'],
        'starting_character': ['Washerwoman', 'Washerwoman', 'Recluse', 'Imp'],
        'script_type': ['tb', 'bmr', 'snv', 'custom'],
        'death': ['True', 'False', 'True', 'False'],
        'death_type': ['Day', 'None', 'Night', 'None']
    })

        totalGoodGames, totalEvilGames, totalGoodWins, totalEvilWins, \
        startingGoodGames, startingEvilGames, goodTeamWins, evilTeamWins, noChangeGames, \
        characterChangeGames, alignmentChangeGames, allChangeGames, totalTownsfolkGames, \
        totalOutsiderGames, totalMinionGames, totalDemonGames, totalTravellerGames, \
        totalTownsfolkWins, totalOutsiderWins, totalMinionWins, totalDemonWins, \
        totalTravellerWins, startingTownsfolkGames, startingOutsiderGames, \
        startingMinionGames, startingDemonGames, startingTravellerGames, \
        charactersPlayed, startingCharactersPlayed, totalTBGames, totalBMRGames, \
        totalSNVGames, totalCustomGames, TBGamesWon, BMRGamesWon, SNVGamesWon, \
        CustomGamesWon, totalDeadGames, totalAliveGames, dayDeadGames, nightDeadGames, \
        deadGamesWon, aliveGamesWon, totalGames, totalWins = fetchData(df)

        self.assertEqual(totalGoodGames, 2)
        self.assertEqual(totalEvilGames, 2)
        self.assertEqual(totalGoodWins, 2)
        self.assertEqual(totalEvilWins, 1)
        self.assertEqual(startingGoodGames, 4)
        self.assertEqual(startingEvilGames, 0)
        self.assertEqual(goodTeamWins, 3)
        self.assertEqual(evilTeamWins, 1)

        self.assertEqual(noChangeGames, 1)
        self.assertEqual(characterChangeGames, 1)
        self.assertEqual(alignmentChangeGames, 1)
        self.assertEqual(allChangeGames, 1)

        self.assertEqual(totalTownsfolkGames, 1)
        self.assertEqual(totalOutsiderGames, 1)
        self.assertEqual(totalMinionGames, 1)
        self.assertEqual(totalDemonGames, 1)
        self.assertEqual(totalTravellerGames, 0)

        self.assertEqual(totalTownsfolkWins, 1)
        self.assertEqual(totalOutsiderWins, 0)
        self.assertEqual(totalMinionWins, 1)
        self.assertEqual(totalDemonWins, 1)
        self.assertEqual(totalTravellerWins, 0)

        self.assertEqual(startingTownsfolkGames, 2)
        self.assertEqual(startingOutsiderGames, 1)
        self.assertEqual(startingMinionGames, 0)
        self.assertEqual(startingDemonGames, 1)
        self.assertEqual(startingTravellerGames, 0)

        self.assertEqual(totalTBGames, 1)
        self.assertEqual(totalBMRGames, 1)
        self.assertEqual(totalSNVGames, 1)
        self.assertEqual(totalCustomGames, 1)

        self.assertEqual(TBGamesWon, 1)
        self.assertEqual(BMRGamesWon, 0)
        self.assertEqual(SNVGamesWon, 1)
        self.assertEqual(CustomGamesWon, 1)

        self.assertEqual(totalDeadGames, 2)
        self.assertEqual(totalAliveGames, 2)
        self.assertEqual(dayDeadGames, 1)
        self.assertEqual(nightDeadGames, 1)
        self.assertEqual(deadGamesWon, 2)
        self.assertEqual(aliveGamesWon, 1)
        self.assertEqual(totalGames, 4)
        self.assertEqual(totalWins, 3)

        # Value count checks
        self.assertEqual(charactersPlayed['Washerwoman'], 1)
        self.assertEqual(startingCharactersPlayed['Washerwoman'], 2)
        self.assertEqual(charactersPlayed['Recluse'], 1)
        self.assertEqual(startingCharactersPlayed['Imp'], 1)

if __name__ == '__main__':
    unittest.main()