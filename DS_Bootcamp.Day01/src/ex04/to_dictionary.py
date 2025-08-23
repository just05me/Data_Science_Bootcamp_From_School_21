def get_dict():
  list_of_tuples = [
  ('Russia', '25'),
  ('France', '132'),
  ('Germany', '132'),
  ('Spain', '178'),
  ('Italy', '162'),
  ('Portugal', '17'),
  ('Finland', '3'),
  ('Hungary', '2'),
  ('The Netherlands', '28'),
  ('The USA', '610'),
  ('The United Kingdom', '95'),
  ('China', '83'),
  ('Iran', '76'),
  ('Turkey', '65'),
  ('Belgium', '34'),
  ('Canada', '28'),
  ('Switzerland', '26'),
  ('Brazil', '25'),
  ('Austria', '14'),
  ('Israel', '12')
  ]
  
  res = {}

  for i in list_of_tuples:
    if i[1] in res:   res[i[1]].append(i[0])

    else:   res[i[1]] = [i[0]]

  return res


def output(val: dict):
    for key in val.keys():
      for value in val[key]:
        print(f"'{key}' : '{value}'")


def main():
   new_dict = get_dict()

   output(new_dict)


if __name__ == "__main__":
    main()