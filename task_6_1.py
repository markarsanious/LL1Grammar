import argparse


def parse_grammar(file):
    input_rules_dict = dict()
    input_first_dict = dict()
    input_follow_dict = dict()
    with open(file, "r") as file:
        lines = file.readlines()
        lines = [[element.strip() for element in line.replace("\n","").split(":")] for line in lines]
        for line in lines:
            rule_to = [element.strip() for element in line[1].split("|")]
            input_rules_dict[line[0]] = rule_to
            input_first_dict[line[0]] = line[2].strip().split(" ")
            input_follow_dict[line[0]] = line[3].strip().split(" ")
    return input_rules_dict, input_first_dict, input_follow_dict

def get_alpha(file):
    alpha =[]
    with open(file, "r") as file:
        lines = file.readlines()
        lines = [[element.strip() for element in line.replace("\n", "").split(":")] for line in lines]
        rules=[]
        # print(lines)
        for line in lines:
            rules.append(line[1])

        rules = [rule.replace("| ", "").split(" ") for rule in rules]
        for rule in rules:
            for letter in rule:
                if not letter[0].isupper() and letter not in alpha:
                    alpha.append(letter)
    return alpha

def epsilon_in_prod_first(production, first):
    output = True
    for letter in production:
        if (not letter[0].isupper() and not letter == 'epsilon') or (letter[0].isupper() and 'epsilon' not in first[letter]):
            output = False
    return output

def epsilon_in_variable_first(variable, rules, first):
    output = True
    prods = rules[variable]
    if 'epsilon' in prods:
        return True
    else:
        for prod in prods:
            prod_array = prod.split(" ")
            for letter in prod_array:
                if (letter[0].isupper() and 'epsilon' not in first[letter]) or letter[0].islower():
                    return False
    return output


def construct_parsing_table(rules, first, follow, alpha):
    # print("RULES", rules)
    # print("FIRST", first)
    # print("FOLLOW", follow)
    if 'epsilon' in alpha:
        alpha.remove('epsilon')
    alpha.append("$")
    table = dict()
    #initialize empty table
    for variable in list(rules.keys()):
        table[variable] = dict()
        for letter in alpha:
            table[variable][letter] = []

    for variable_rules in rules:
        for index, rule in enumerate(rules[variable_rules]):
            prod = rules[variable_rules][index].split(" ")
            for letter in alpha:
                if not prod[0][0].isupper() and not prod == 'epsilon' and letter == prod[0]:
                    table[variable_rules][letter].append(" ".join(prod))
                if prod[0][0].isupper() and letter in first[prod[0]]:
                    table[variable_rules][letter].append(" ".join(prod))
                if prod[0][0].isupper() and epsilon_in_prod_first(prod, first) and letter in follow[rules[variable_rules]]:
                    table[variable_rules][letter].append(" ".join(prod))
                if epsilon_in_variable_first(variable_rules, rules, first) and letter in follow[variable_rules]:
                    table[variable_rules][letter].append("epsilon")
                table[variable_rules][letter] = list(set(table[variable_rules][letter]))
    return table

def valid_table(table):
    for row in table:
        for col in table[row]:
            if len(table[row][col]) > 1:
                return False
    return True

def print_output_table(table, output_file):
    if valid_table(table):
        for row in table:
            for col in table[row]:
                output = ""
                if len(table[row][col]) > 0:
                    output = table[row][col][0]
                output_file.write(row + " : " + col + " : " + output + "\n")
    else:
        output_file.write("invalid LL(1) grammar\n")

def top_of_stack(stack):
    return stack[len(stack)-1]



def execute_input(table, file, start_variable):
    with open(file, "r") as file:
        input_text = file.readline()
        input_text = input_text.split(" ")
        input_text.append('$')

    stack = ['$', start_variable]
    counter = 0
    while counter < len(input_text):
        x = input_text[counter]
        y = stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        if x == '$' and y == '$':
            return True
        elif not y.isupper() and not x == y:
            counter +=1
            return False
        elif y.isupper():
            prods = table[y][x][0].strip()
            prods_array = prods.split(" ")
            for i in range(len(prods_array)-1, -1, -1):
                if not(prods_array[i] == 'epsilon'):
                    stack.append(prods_array[i])
        elif x == '$' and not y.isupper() and not y == '$':
            return False
        elif y == '$' and not x == '$':
            return False
        elif not y.isupper() and x == y:
            counter += 1
            continue
    return True


def print_output_to_file(input_rules_map, output_file):
    for rule in input_rules_map:
        output_file.write(rule + " : " + ' '.join(input_rules_map[rule][0]) + " : " + ' '.join(input_rules_map[rule][1]) + "\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--grammar', action="store", help="path of file to take as input to read grammar",
                        nargs="?", metavar="dfa_file")
    parser.add_argument('--input', action="store", help="path of file to take as input to test strings on LL table",
                        nargs="?", metavar="input_file")

    args = parser.parse_args()
    output_file_1 = open("task_6_1_result.txt", "w+")
    output_file_2 = open("task_6_2_result.txt", "w+")

    input_rules_map, input_first_dict, input_follow_dict = parse_grammar(args.grammar)
    alpha = get_alpha(args.grammar)
    table = construct_parsing_table(input_rules_map, input_first_dict, input_follow_dict, alpha)
    print_output_table(table, output_file_1)

    start_variable = list(table.keys())[0]

    output = False
    if valid_table(table):
        output = execute_input(table, args.input, start_variable)

    if output:
        output_file_2.write("yes")
    else:
        output_file_2.write("no")




