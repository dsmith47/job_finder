class TextUtils():
  # slices list at x and returns left hand side
  def lhs(l, x):
    return l[:x]

  # slices list at x and returns right hand side
  def rhs(l, x):
    return l[x:]

  # find first instance of search_str and return lhs
  def seek_from_start_lhs(l, search_str):
    i = 0
    while i < len(l) and l[i] != search_str:
      i += 1
    if i == len(l): i = 0
    return TextUtils.lhs(l, i)
 
  # find first instance of search_str and return rhs
  def seek_from_start_rhs(l, search_str):
    i = 0
    while i < len(l) and l[i] != search_str:
      i += 1
    if i == len(l): i = 0
    return TextUtils.rhs(l, i)   
 
  # find last instance of search_str and return lhs
  def seek_from_end_lhs(l, search_str):
    i = len(l) - 1
    while i > 0 and l[i] != search_str:
      i -= 1
    if i == 0: i = len(l) - 1
    return TextUtils.lhs(l, i)
