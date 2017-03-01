# Send test messages to the local ActiveMQ server
import stomp


TARGET_DIR = 'C:\\\\Users\\\\marcs\\\\Developer\\\\Diamond\\\\diamond-imagematch\\\\test-images\\\\Focus Stacking\\\\VMXI-AA0019-H01-1-R0DRP1\\\\levels'
OUTPUT_PATH = 'C:\\\\Users\\\\marcs\\\\Desktop\\\\test\\\\test_'

# Network example
# TARGET_DIR = '/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test'
# OUTPUT_PATH = '/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test/output_'

EXTENSION = 'tif'

connection = stomp.Connection(host_and_ports=[("localhost", 61613)])
connection.start()
connection.connect(wait=True)
# request = '{' \
#           '"job_id": "test_job",' \
#           '"target_dir": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test",' \
#           '"output_path": ""' \
#           '}'

for i in range(0, 10):
    request = '{' \
              '"job_id": "test_job",' \
              '"target_dir": "' + TARGET_DIR + '",' \
              '"output_path": "' + OUTPUT_PATH + str(i) + '.' + EXTENSION + '"' \
              '}'
    connection.send("/queue/vmxi_extended_focus_service.input", request, headers={"job_id": "test_job"})
connection.disconnect()

