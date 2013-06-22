import contextlib
import csv
import datetime
import glob
import json
import re

RE_ACTIVITY = re.compile(r'data\-\d+\-(.*?).txt')

TRAINING_SET_PERCENT = .67

with open('training.csv', 'wb') as training_file:
    with open('test.csv', 'wb') as test_file:
        training_writer = csv.writer(training_file)
        test_writer = csv.writer(test_file)
        training_writer.writerow(['activity','x','y','z','alpha','beta','gamma','ts'])
        training_writer.writerow(['string','float','float','float','float','float','float','datetime'])
        training_writer.writerow(['S','','','','','','T'])
        test_writer.writerow(['activity','x','y','z','alpha','beta','gamma','ts'])
        test_writer.writerow(['string','float','float','float','float','float','float','datetime'])
        test_writer.writerow(['S','','','','','','T'])
        for srcfilename in glob.glob('data/*.txt'):
            with open(srcfilename, 'r') as srcfile:
                src = json.load(srcfile)
            activity = RE_ACTIVITY.findall(srcfilename)[0].replace(' ', '_')
            print activity, len(src)
            for row in src[:int(len(src) * TRAINING_SET_PERCENT)]:
                training_writer.writerow(
                    [
                        activity,
                        row['accelerationIncludingGravity']['x'],
                        row['accelerationIncludingGravity']['y'],
                        row['accelerationIncludingGravity']['z'],
                        row['rotationRate']['alpha'],
                        row['rotationRate']['beta'],
                        row['rotationRate']['gamma'],
                        datetime.datetime.fromtimestamp(row['ts']/1000).isoformat()
                    ]
                )
            for row in src[int(len(src) * TRAINING_SET_PERCENT):]:
                test_writer.writerow(
                    [
                        activity,
                        row['accelerationIncludingGravity']['x'],
                        row['accelerationIncludingGravity']['y'],
                        row['accelerationIncludingGravity']['z'],
                        row['rotationRate']['alpha'],
                        row['rotationRate']['beta'],
                        row['rotationRate']['gamma'],
                        datetime.datetime.fromtimestamp(row['ts']/1000).isoformat()
                    ]
                )
