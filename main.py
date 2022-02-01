import numpy as np
import string
import pandas as pd


with open('wordle-answers-alphabetical.txt') as f:
    all_answers = f.readlines()
all_answers = [x.replace('\n', '') for x in all_answers]

with open('wordle-allowed-guesses.txt') as f:
    allowed_guesses = f.readlines()
allowed_guesses = [x.replace('\n', '') for x in allowed_guesses]
allowed_guesses.extend(all_answers)


class Wordle:
    def __init__(self, seed=None):
        self.seed = seed
        self.answer = 'null'
        self.all_answers = all_answers
        self.allowed_guesses = allowed_guesses
        self.current_state = [0, 0, 0, 0, 0]
        self.guesses = []
        self.yellows = []
        self.greens = []
        self.grays = []
        self.win = 0

    def pick_answer(self):
        if self.seed is not None:
            np.random.seed(self.seed)
            print('SETTING RANDOM SEED')
        int_pick = np.random.randint(low=0, high=len(self.all_answers))
        self.answer = self.all_answers[int_pick]

    def reset_gamestate(self):
        self.current_state = [0, 0, 0, 0, 0]
        self.yellows = []
        self.greens = []
        self.grays = []
        self.guesses = []

    def evaluate_guess(self, guess):
        if guess not in self.allowed_guesses:
            print('{} is not a valid guess'.format(guess))
            return

        self.guesses.append(guess)
        if len(self.guesses) > 6:
            self.guesses.remove(guess)
            print('You have no more guesses remaining')
            return

        print('Evaluating Guess: {}'.format(guess))
        # first look for greens
        for i, letter_guess in enumerate(guess):
            for j, letter_answer in enumerate(self.answer):
                if i == j and letter_guess == letter_answer:
                    if (i, letter_guess) not in self.greens:
                        self.greens.append((i, letter_guess))

        # check to see if you won
        if len(self.greens) == 5:
            print('You win! The word was {}'.format(self.answer))
            self.win = 1
        else:
            # clean out any yellows that have become greens
            if len(self.yellows) > 0:
                removes = []
                for green in self.greens:
                    letter_green = green[1]
                    for yellow in self.yellows:
                        letter_yellow = yellow[1]
                        if letter_green == letter_yellow:
                            # make sure a letter doesnt get put in twice
                            if yellow[1] not in [x[1] for x in removes]:
                                removes.append(yellow)
                if len(removes) > 0:
                    for rmv in removes:
                        self.yellows.remove(rmv)

            # now look for yellows
            for i, letter_guess in enumerate(guess):
                if letter_guess in self.answer:
                    if letter_guess not in [x[1] for x in self.greens]:
                        self.yellows.append((i, letter_guess))


            # now look for grays
            for letter_guess in guess:
                if letter_guess not in self.answer:
                    self.grays.append(letter_guess)


            print('Number of Guesses: {}'.format(len(self.guesses)))
            print('Green Letters: {}'.format(self.greens))
            print('Yellow Letters: {}'.format(self.yellows))
            print('Gray Letters: {}'.format(self.grays))




class SolverV1:
    """
    This solver aims to make good guesses by simply calculating the best guess
    as a function of how much it can reduce the list with each guess.
    """
    def __init__(self):
        self.allowed_guesses = allowed_guesses
        self.remaining_allowed_guesses = allowed_guesses
        self.guess_num = 0
        self.past_guesses = []
        self.greens = []
        self.yellows = []
        self.grays = []

    def reset(self):
        self.__init__()

    def get_gamestate(self, wordle):
        self.greens = wordle.greens
        self.yellows = wordle.yellows
        self.grays = wordle.grays

    def _remove_known_bad_guesses(self):
        old_remainder = self.remaining_allowed_guesses
        new_remainder = old_remainder
        # remove your last guess
        if len(self.past_guesses) > 0:
            if self.past_guesses[-1] in new_remainder:
                new_remainder.remove(self.past_guesses[-1])

        # remove all the grays
        new_remainder = [word for word in new_remainder if not any(
            letter in word for letter in self.grays
        )]

        # remove all the words that dont have yellows and greens
        y_and_g_letters = []
        if len(self.greens) > 0:
            green_letters = [x[1] for x in self.greens]
            y_and_g_letters.extend(green_letters)

        if len(self.yellows) > 0:
            yellow_letters = [x[1] for x in self.yellows]
            y_and_g_letters.extend(yellow_letters)

        if len(y_and_g_letters) > 0:
            new_remainder = [word for word in new_remainder if all(
                letter in word for letter in y_and_g_letters
            )]

        # make sure you dont use yellows in the same place as before.
        if len(self.yellows) > 0:
            for yellow in self.yellows:
                idx = yellow[0]
                letter = yellow[1]
                new_remainder = [word for word in new_remainder if word[idx]!=letter]

        # make sure the greens are positioned
        if len(self.greens) > 0:
            for green in self.greens:
                idx = green[0]
                letter = green[1]
                new_remainder = [word for word in new_remainder if word[idx]==letter]

        self.remaining_allowed_guesses = new_remainder


    def _score_words(self, wordlist):
        """
        This will generate the score for each word in a list based on letter frequency
        :return:
        """
        # recalculate letter frequencies
        letter_freq_dict = dict.fromkeys(string.ascii_lowercase, 0)
        for word in wordlist:
            l = len(word)  # should be 5
            if l != 5:
                print('BAD WORD IN LIST: {}'.format(word))
                break

            for letter in word:
                letter_freq_dict[letter] += 1

        # now use frequencies to generate new scores
        word_scores = dict.fromkeys(wordlist, 0)
        for word in wordlist:
            score = 0
            unique_letters = list(set(word))
            for letter in unique_letters:
                score += letter_freq_dict[letter]
            word_scores[word] = score

        return pd.Series(word_scores)

    def update_guess(self):
        self._remove_known_bad_guesses()
        remaining_words = self.remaining_allowed_guesses
        word_scores = self._score_words(remaining_words)
        word_scores = word_scores.sort_values(ascending=False)
        print(word_scores.head())
        return word_scores.index[0]








if __name__ == '__main__':
    #wrdl = Wordle()
    #wrdl.pick_answer()
    #wrdl.answer = 'black'
    #print(wrdl.answer)

    #wrdl.evaluate_guess('drave')
    #wrdl.evaluate_guess('savoy')


    #solver = SolverV1()
    #solver.get_gamestate(wrdl)
    #print(solver.greens)
    #print(solver.yellows)
    #print(solver.grays)

    #guess1 = solver.update_guess()

    #wrdl.evaluate_guess(guess1)
    #solver.get_gamestate(wrdl)
    #print(solver.greens)
    #print(solver.yellows)
    #print(solver.grays)

    #guess2 = solver.update_guess()

    #wrdl.evaluate_guess(guess2)
    #solver.get_gamestate(wrdl)
    #print(solver.greens)
    #print(solver.yellows)
    #print(solver.grays)

    results = {}

    for i in range(2315):
        wrdl = Wordle()
        wrdl.reset_gamestate()
        wrdl.pick_answer()
        #wrdl.answer = 'foyer'
        print('**** STARTING NEW GAME ****')
        print('Answer is: {}'.format(wrdl.answer))
        solver = SolverV1()

        for j in range(6):
            if wrdl.win == 1:
                continue
            guess = solver.update_guess()
            wrdl.evaluate_guess(guess)
            solver.get_gamestate(wrdl)
            if wrdl.win == 1:
                results[wrdl.answer] = 1
            if j == 5 and wrdl.win == 0:
                results[wrdl.answer] = 0

    total_games = len(results)
    won_games = sum(list(results.values()))
    win_pct = won_games / total_games
    print('')
    print('')
    print('Your win % was: {} %'.format(win_pct * 100))








