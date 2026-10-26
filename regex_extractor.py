import re
import pendulum as pend

def get_date_re(expression:str):
    pattern1 = r"(?i)(in|after)( |_)*([0-9]+)( |_)*(day|week|month|year)s?"
    match = re.search(pattern1, expression)
    if match:
        # prints the number in the text
        # print(match.group(3))
        # FOR THE LOVE OF GOD FIND A BETTER WAY THAN THIS FUCKING SHIT
        # I LOSE YEARS OF MY LIFE EVERY TIME I LOOK AT THIS
        if match.group(5).lower() == 'day':
            return match.group(0), pend.now().add(days = int(match.group(3)))
        elif match.group(5).lower() == 'week':
            return match.group(0), pend.now().add(weeks = int(match.group(3)))
        elif match.group(5).lower() == 'month':
            return match.group(0), pend.now().add(months = int(match.group(3)))
        elif match.group(5).lower() == 'year':            
            return match.group(0), pend.now().add(years = int(match.group(3)))
        else:
            return "", pend.now()
        # return pend.now().add(days = int(match.group(3)))
    pattern2 = r"((next|n)( |_)?)+(sat|sun|mon|tue|wed|thu|fri)"
    match = re.search(pattern2, expression)
    if match:
        week_arr = ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri']
        day = match.group(4)
        today = pend.now().format('ddd').lower()
        # calculate the number of days between the expression day and today
        no_days = week_arr.index(day) - week_arr.index(today)
        if no_days <= 0:
            no_days += 7
        # calculate the number of weeks
        no_weeks = match.group(0).replace(match.group(4),'').count('n') - 1
        return match.group(0), pend.now().add(days = no_days, weeks = no_weeks)
    else:
        # in case of no match fall back to
        return "", pend.now()

def get_priority_re(expression:str):
    pattern1 = r"(!|(p(:|_|-)|(pr|prior|priority)(| |:|_|-)))(high|h|mid|m|low|l|1|2|3)"
    pattern1s = r"!(high|h|mid|m|low|l|1|2|3)"
    match = re.search(pattern1s, expression)
    if match:
        priority = 0
        if match.group(1).lower().startswith('h') or match.group(1) == '1':
            priority = 1
        elif match.group(1).lower().startswith('m') or match.group(1) == '2':
            priority = 2
        elif match.group(1).lower().startswith('l') or match.group(1) == '3':
            priority = 3
        return match.group(0), priority
    else:
        # in case of no match falls back to
        return '', 0

def get_info_re(expression:str) -> tuple[str, dict]:
    """
      gets the info [deadline, priority] out of the expression and returns
      a tuple of the expression after removing the info parts from it and
      a list of the info 
    """
    expression_done: str = expression
    deadline_expression, deadline = get_date_re(expression)
    # print(deadline_expression, deadline)
    expression_done = expression_done.replace(str(deadline_expression), "", 1)
    priority_expression, priority = get_priority_re(expression)
    # print(priority_expression, priority)
    expression_done = expression_done.replace(str(priority_expression), "", 1)
    # print(expression_done)
    return expression_done, {"deadline": deadline, "priority": priority}
        

def main():
    # TEST

    # # test pattern 1
    # print("PATTERN 1")
    # print(get_date_re('in 2 days'))
    # print(get_date_re('in_2_days'))
    # print(get_date_re('in 1 day'))
    # print(get_date_re('in2days'))
    # print(get_date_re('IN2DAYS'))

    # # test pattern 2
    # print("PATTERN 2")
    # print(get_date_re('next mon'))
    # print(get_date_re('next_wed'))
    # print(get_date_re('next next mon'))
    # print(get_date_re('nnnn mon'))
    # print(get_date_re('nextn_next mon'))
    # print(get_date_re('n mon'))

    # print("LONG PHRASES")
    # print(get_date_re('This task is due next mon'))

    # print("PRIORITY")
    # print(get_priority_re("!high"))
    # print(get_priority_re("!m"))
    # print(get_priority_re("!3"))

    # print("THE 2 TOGETHER")
    # s = "something something next fri !high"
    # print(get_date_re(s))
    # print(get_priority_re(s))

    s = 'sth sth next fri !high'
    print(get_info_re(s))
    # match = re.search( r"!high", s)
    # print(match.group(0))
    # print(s.replace(match.group(0), "", 1))
    s = 'nothing'
    print(get_info_re(s))
    
if __name__ == "__main__":
    main()
