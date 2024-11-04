import os

# Открываем файл
with open('db/Прайс НОВЫЙ.csv', 'r', errors='ignore') as file:
    file = [sent.replace(';', '') for sent in file.readlines()]
    #print(*file, sep='\n')



def process_array_linear(array):
    depth = 0

    i = 0
    price_list = []
    for item in array:
        item = item.replace('\n', '')
        if '{1}' in item:
            price_list.append([item.replace('{1}', '')])
            depth += 1
        elif '{2}' in item:
            price_list[-1].append([item.replace('{2}', '')])
            depth += 1
        elif '{3}' in item:
            price_list[-1][-1].append([item.replace('{3}', '')])
            depth += 1
        elif '{4}' in item:
            price_list[-1][-1][-1].append([item.replace('{4}', '')])
            depth += 1
        else:
            if depth == 1:
                price_list[-1].append(item)
            if depth == 2:
                price_list[-1][-1].append(item)
            if depth == 3:
                price_list[-1][-1][-1].append(item)

    return price_list


class category:

    def __init__(self, name='', subcategories=None, values=None, sub=0, depth=0):
        if values is None:
            values = []
        if subcategories is None:
            subcategories = []
        self.name = name
        self.subcategories = subcategories
        self.values = values
        self.sub = sub
        self.depth = depth

    def subs_names(self):
        a = '['
        for i in range(len(self.subcategories)):
            a += self.subcategories[i].name + ', '
        return a[:-1]+']'

    def define(self, lines):
        d = ['{1}', '{2}', '{3}', '{4}']
        if any(i in lines[0] for i in d):
            self.sub = 1
        else:
            self.sub = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<< Class category, name: ' + self.name + ' subs: ' + self.subs_names() +'>>'

    def process_lines(self, lines):
        self.define(lines)
        if self.sub:
            counter = 0
            for line in lines:
                if '{' + str(self.depth) + '}' in line or \
                        '{' + str(self.depth - 1) + '}' in line or \
                        '{' + str(self.depth - 2) + '}' in line or \
                        '{' + str(self.depth - 3) + '}' in line:
                    break
                if '{' + str(self.depth + 1) + '}' in line:
                    self.subcategories.append(
                        category(name=line.replace('{' + str(self.depth + 1) + '}', '').replace('\n', ''),
                                 depth=self.depth + 1))
                    self.subcategories[-1].process_lines(lines[counter+1:])
                counter += 1
        else:
            for line in lines:
                if '{' + str(self.depth) + '}' in line or \
                        '{' + str(self.depth - 1) + '}' in line or \
                        '{' + str(self.depth - 2) + '}' in line or \
                        '{' + str(self.depth - 3) + '}' in line:
                    break
                self.values.append(line)

    def get_items(self):
        if self.sub:
            return [item for item in self.subcategories]
        else:
            return [item for item in self.values]


Price = category()

#Price = process_array_linear(file)
# print(Price)
# print(Price[0])


Price.process_lines(file)
