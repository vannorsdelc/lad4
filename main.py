# CS 1430 - Betweener
#
# Run this program, type an age, and read what it prints.
# Change only the lines under the two "yours" markers.

##############
# CONSTANTS
##############
LOW_AGE = 18
HIGH_AGE = 21
AGE_PROMPT = "Please enter an age --> "

user_age = int(input(AGE_PROMPT))

print("--- Part 1: given ---")
if user_age >= LOW_AGE:
    if user_age < HIGH_AGE:
        print("BETWEENER")

print("--- Part 1: yours ---")


print("--- Part 2: given ---")
if user_age < LOW_AGE:
    print("NOT BETWEENER")
else:
    if user_age >= HIGH_AGE:
        print("NOT BETWEENER")

print("--- Part 2: yours ---")

user_age = int(input(AGE_PROMPT))

print("--- Part 1: given ---")
if user_age >= LOW_AGE and user_age < HIGH_AGE:
        print("BETWEENER")

print("--- Part 1: yours ---")


print("--- Part 2: given ---")
if user_age < LOW_AGE or user_age >= HIGH_AGE:
    print("NOT BETWEENER")

print("--- Part 2: yours ---")
