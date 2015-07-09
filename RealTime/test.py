class Time_data:
    def __init__(self):
        self.list_time_start_record = []
        self.list_time_end_record = []
        self.list_time_start_sending = []
        self.list_time_end_sending = []
        self.list_time_first_result = []
        self.list_time_final_result = [] 

    def add_record(self,data,content_type):
        if content_type=="start":
            self.list_time_start_record.append(data)
            return
        if content_type=="end":
            self.list_time_end_record.append(data)
        else:
            print "* Error trying to add time for recording"
            

    def add_sending(self,data,content_type):
        if content_type=="start":
            self.list_time_start_sending.append(data)
            return
        if content_type=="end":
            self.list_time_end_sending.append(data)
        else:
            print "* Error trying to add time for sending"

    def add_result(self,data,content_type):
        if content_type=="first":
            self.list_time_first_result.append(data)
            return
        if content_type=="final":
            self.list_time_final_result.append(data)
        else:
            print "* Error trying to add time for result"

    def get_time(self,content,content_type,k):
        if k=="last":
            if content=="result":
                if content_type=="first":
                    return self.list_time_first_result[len(self.list_time_first_result)-1]
                if content_type=="final":
                    return self.list_time_final_result[len(self.list_time_final_result)-1]

            if content=="record":
                if content_type=="start":
                    return self.list_time_start_record[len(self.list_time_start_record)-1]
                if content_type=="end":
                    return self.list_time_end_record[len(self.list_time_end_record)-1]

            if content=="sending":
                if content_type=="start":
                    return self.list_time_start_sending[len(self.list_time_start_sending)-1]
                if content_type=="end":
                    return self.list_time_end_sending[len(self.list_time_end_sending)-1]

        if isinstance( k, int ):
            if content=="result":
                if content_type=="first":
                    return self.list_time_first_result[k]
                if content_type=="final":
                    return self.list_time_final_result[k]

            if content=="record":
                if content_type=="start":
                    return self.list_time_start_record[k]
                if content_type=="end":
                    return self.list_time_end_record[k]

            if content=="sending":
                if content_type=="start":
                    return self.list_time_start_sending[k]
                if content_type=="end":
                    return self.list_time_end_sending[k]


        print "Error using get_time of class Time_data"
        return 

def main():
    time_data = Time_data()
    time_data.add_record(15,"start")
    time_data.add_record(15453454,"start")
    time_data.add_sending(12,"start")
    time_data.add_result(4534,"first")
    time_data.add_result(453484,"final")
    time_data.add_result(445345420424254245,"first")

    print time_data.get_time("result","final","last")


if __name__ == '__main__':
    main()