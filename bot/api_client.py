import requests, json, logging
from datetime import datetime
from config_updated import API_FULL_URL

logger = logging.getLogger(__name__)

def calculate_days(admission_date, discharge_date):
    try:
        ap = admission_date.split('-')
        dp = discharge_date.split('-')
        if len(ap)==3 and len(dp)==3:
            a = datetime(int(ap[2]),int(ap[1]),int(ap[0]))
            d = datetime(int(dp[2]),int(dp[1]),int(dp[0]))
            return max(1, (d-a).days+1)
        return 1
    except: return 1

def generate_leave_id(id_number, admission_date, discharge_date):
    try:
        ip = id_number[-4:] if len(id_number)>=4 else id_number
        an = ''.join(filter(str.isdigit, admission_date))[-3:]
        dn = ''.join(filter(str.isdigit, discharge_date))[-4:]
        ln = (ip+an+dn).ljust(11,'0')[:11]
        return f"PSL{ln}"
    except: return f"PSL{id_number[-4:]}0000000"

def convert_date_format(d):
    try:
        p=d.split('-')
        return f"{p[2]}-{p[1]}-{p[0]}" if len(p)==3 else d
    except: return d

def send_leave_data_to_api(user_data):
    try:
        leave_id = generate_leave_id(user_data.get('id_number',''),user_data.get('admission_date_gregorian',''),user_data.get('discharge_date_gregorian',''))
        api_data = {
            'service_code': leave_id,
            'identity_number': user_data.get('id_number',''),
            'patient_name_ar': user_data.get('patient_name_ar',''),
            'patient_name_en': user_data.get('patient_name_en',''),
            'nationality_ar': user_data.get('nationality_ar',''),
            'nationality_en': user_data.get('nationality_en',''),
            'workplace_ar': user_data.get('employer_ar',''),
            'workplace_en': user_data.get('employer_en',''),
            'doctor_name_ar': user_data.get('doctor_name_ar',''),
            'doctor_name_en': user_data.get('doctor_name_en',''),
            'job_title_ar': user_data.get('position_ar',''),
            'job_title_en': user_data.get('position_en',''),
            'admission_date_gregorian': convert_date_format(user_data.get('admission_date_gregorian','')),
            'admission_date_hijri': user_data.get('admission_date_hijri',''),
            'discharge_date_gregorian': convert_date_format(user_data.get('discharge_date_gregorian','')),
            'discharge_date_hijri': user_data.get('discharge_date_hijri',''),
            'report_issue_date': convert_date_format(user_data.get('issue_date_gregorian','')),
            'facility_name_ar': user_data.get('hospital_name_ar',''),
            'facility_name_en': user_data.get('hospital_name_en',''),
            'report_time': user_data.get('time','00:00:00'),
            'duration_days': calculate_days(user_data.get('admission_date_gregorian',''),user_data.get('discharge_date_gregorian',''))
        }
        logger.info(f"API URL: {API_FULL_URL}")
        r = requests.post(API_FULL_URL, json=api_data, headers={'Content-Type':'application/json'}, timeout=30)
        if r.status_code in [200,201]:
            return {'success':True,'message':'تم حفظ البيانات','leave_id':leave_id}
        else:
            return {'success':False,'message':f'خطأ HTTP {r.status_code}','leave_id':leave_id}
    except Exception as e:
        return {'success':False,'message':str(e),'leave_id':leave_id if 'leave_id' in locals() else ''}
