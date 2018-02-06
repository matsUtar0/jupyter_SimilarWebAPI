import sys,subprocess,csv

args = sys.argv

file_name = args[1]
start_date = args[2]
end_date = args[3]

with open(file_name,'r') as f:
    for row in f:
        url = row.rstrip()
        call = ['python', 'SimilarWebAPI.py', url, start_date, end_date]
        try:
            res = subprocess.check_call(call)
            print(url + 'の抽出完了')
        except:
            print('Error')

