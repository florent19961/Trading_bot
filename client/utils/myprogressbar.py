
class ProgressBar():
    def __init__(self, task):
        self.task = task
        self.total_length = 50
        self.last_step = 0
        print('Starting task : ' + task)
        return
    
    def show_progress(self, progress):
        number_of_completed_element = int(progress * self.total_length)
        number_of_uncomplete = self.total_length - number_of_completed_element
        list_of_element = ['['] + ['-'] * number_of_completed_element + [' '] * number_of_uncomplete + [']']
        if self.last_step != round(progress,3):
            string_to_show = ''.join(list_of_element) + '   ' + '{:.1%}'.format(progress)
            self.last_step = round(progress,3)
            print(string_to_show, end='\r')

    def finish(self):
        string_to_show = '[' + ''.join(['-'] * self.total_length) + ']     100%'
        print(string_to_show)
        print('Finished task : ' + self.task)

if __name__ == '__main__':
    import time
    pb = ProgressBar('Testing my ProgressBar')
    time.sleep(0.2)
    pb.show_progress(0.01)
    time.sleep(0.2)
    pb.show_progress(0.215)
    time.sleep(0.2)
    pb.show_progress(0.5)
    time.sleep(0.2)
    pb.show_progress(0.67998)
    time.sleep(0.2)
    pb.show_progress(0.95)
    time.sleep(0.2)
    pb.finish()