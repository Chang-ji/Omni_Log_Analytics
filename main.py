import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os
from tkinter import filedialog
from tkinter import *
import math

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
font_path = r'./godoMaum.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

def makedirs(path):
   try:
        os.makedirs(path)
   except OSError:
       if not os.path.isdir(path):
           raise

def stringtobyte(data):
    length = 2
    byte_two = [data[i:i + length] for i in range(0, len(data), length)]
    for i in range(len(byte_two)):
        byte_two[i] = chr(int(byte_two[i], 16))

    return ''.join(byte_two)

# 로그 데이터 위치 열람하는 함수
def datapathAndanaytics(dir_path):
    print(dir_path)
    if not dir_path:
        return
    path_list = []
    for (root, directories, files) in os.walk(dir_path):
        for file in files:
            if 'ChargerLog.log' in file:
                file_path = os.path.join(root, file)
                path_list.append(file_path)

    if len(path_list) == 0:
        return

    # 로그 분석하는 부분
    for path_one in path_list:
        logDataAnayltics(path_one)
    print("데이터 모두 분석완료")


def logDataAnayltics(fie_path):
    board_receive_data = []
    server_send_data = []
    payment_data = []
    wattage_wattage_data, wattage_volt_ampere_data = [], []

    with open(fie_path, 'rt') as file:
        data_line = file.readlines()
        file_name = data_line[0].strip()[:13]
        for data in data_line:
            data_one = data.strip()

            # 전력량계 전력량 데이터 프레임 만들기
            if '[Wattage]' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 현 전력량, 전 전력량, 전전 전력량
                list_second_data = list_data[1].split(' | ')
                wattage = round(float(list_second_data[1]), 2)
                pre_wattage = round(float(list_second_data[3]), 2)
                pre_pre_wattage = round(float(list_second_data[5]), 2)

                # 데이터 프레임 만들기
                wattage_wattage_data.append([cg_date_time, wattage, pre_wattage, pre_pre_wattage])
            # 전력량계 전압 전류 데이터 프레임 만들기
            elif '[VoltAndAmpere]' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 전압 전류
                list_second_data = list_data[1].split(' | ')
                volt = round(float(list_second_data[1]), 2)
                ampere = round(float(list_second_data[3]), 2)

                # 데이터 프레임 만들기
                wattage_volt_ampere_data.append([cg_date_time, volt, ampere])
            # 보드 데이터 c1 리시브 데이터 분석
            elif '[CONTROL_BD_RECEIVE_DATA]' in data_one and '(8c)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                #  패킷에 해당하는 값
                list_second_data = list_data[1].split(' : ')
                #emg 버튼, 충전상태, 오류코드, soc, 출력가능 전압, 출력가능 전류, 충전전압, 충전 전류, 남은시간, 충전 진행 코드
                emg_btn = int(list_second_data[1][18:20])
                charger_status = int(list_second_data[1][20:22])
                error_code = int(list_second_data[1][22:26], 16)
                soc = int(list_second_data[1][26:28], 16)
                enable_volt = int(list_second_data[1][28:32],16) // 10
                enable_ampere = int(list_second_data[1][32:36], 16) // 10
                volt = int(list_second_data[1][36:40], 16)
                ampere = int(list_second_data[1][40:44], 16)
                remain_time = int(list_second_data[1][54:58], 16)
                charging_code = int(list_second_data[1][58:62], 16)

                board_receive_data.append([cg_date_time ,emg_btn, charger_status, error_code, soc, enable_volt, enable_ampere, volt, ampere, remain_time, charging_code, 100])
            # 보드 데이터 f1 기록
            elif '[CONTROL_BD_RECEIVE_DATA]' in data_one and '(8f)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')
                board_receive_data.append([cg_date_time, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200])

            # 옴니 서버 Send 데이터 프레임 만들기
            elif '[OMNI_SERVER_SEND_DATA]' in data_one:
                if '[OMNI_SERVER_SEND_DATA](17)' in data_one:
                    # 시간
                    list_data = data_one.split(' DEBUG ')
                    cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                    # 17 패킷에 해당하는 값
                    list_second_data = list_data[1].split(' : ')

                    # 카드 타입 | 회원 번호 | 충전량 | 충전시간 | 전압 | 암페어 | 상태
                    # cardtype, cardnum, wattage, chargingtime, volt, ampere, state
                    binary_data = list_second_data[1]
                    card_type = chr(int(binary_data[34:36], 16))
                    card_num = stringtobyte(binary_data[38:70])
                    server_send_data.append([cg_date_time, card_type, card_num, 0, 0, 0, 0, 100])
                elif '[OMNI_SERVER_SEND_DATA](19)' in data_one:
                    # 시간
                    list_data = data_one.split(' DEBUG ')
                    cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                    # 19 패킷에 해당하는 값
                    list_second_data = list_data[1].split(' : ')

                    # 카드 타입 | 회원 번호 | 충전량 | 충전시간 | 전압 | 암페어 | 상태
                    binary_data = list_second_data[1]

                    server_send_data.append([cg_date_time, None, None, float(stringtobyte(binary_data.split('7C')[1])) * 1000, int(stringtobyte(binary_data.split('7C')[2])), int(stringtobyte(binary_data.split('7C')[3])), int(stringtobyte(binary_data.split('7C')[4])), 200])
                elif '[OMNI_SERVER_SEND_DATA](1A)' in data_one:
                    # 시간
                    list_data = data_one.split(' DEBUG ')
                    cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                    # 1A 패킷에 해당하는 값
                    list_second_data = list_data[1].split(' : ')

                    # 카드 타입 | 회원 번호 | 충전량 | 충전시간 | 전압 | 암페어 | 상태
                    binary_data = list_second_data[1]
                    binary_divide_7c = binary_data.split('7C')
                    server_send_data.append([cg_date_time, None, stringtobyte(binary_divide_7c[1]), float(stringtobyte(binary_divide_7c[2])) * 1000, int(stringtobyte(binary_divide_7c[3])), None, None, 300])
            # 결제 단말기 데이터 추출
            elif '[SFA_PAYMENT_RECEIVE_DATA]' in data_one and '(6234)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 100, None, None, None, None])
            elif '[SFA_PAYMENT_SEND_DATA]' in data_one and '(4734)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 결제 요금
                list_second_data = list_data[1].split(' : ')[1]
                payment_amount = int(list_second_data[52:60], 16)
                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 200, payment_amount, None, None, None])
            elif '[SFA_PAYMENT_RECEIVE_DATA]' in data_one and '(3447)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 응답코드, 거리일시, 승인번호
                list_second_data = list_data[1].split(' : ')[1]
                payment_code = int(list_second_data[50:52], 16)
                payment_time = list_second_data[52:66]
                payment_approval = int(stringtobyte(list_second_data[66:88]))
                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 300, None, payment_approval, payment_code, payment_time])
            elif '[SFA_PAYMENT_SEND_DATA]' in data_one and '(4F34)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 승인 번호, 취소 요금
                list_second_data = list_data[1].split(' : ')[1]
                payment_cancel_approval_code = int(stringtobyte(list_second_data[50:72]))
                payment_cancel_amount = int(list_second_data[96:104], 16)

                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 400, payment_cancel_amount, payment_cancel_approval_code, None, None])
            elif '[SFA_PAYMENT_RECEIVE_DATA]' in data_one and '(344F)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 응답코드, 거리일시, 승인번호
                list_second_data = list_data[1].split(' : ')[1]
                payment_code = int(list_second_data[50:52], 16)
                payment_time = list_second_data[52:66]
                payment_approval = int(stringtobyte(list_second_data[66:88]))
                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 500, None, payment_approval, payment_code, payment_time])
            elif '[SFA_PAYMENT_SEND_DATA]' in data_one and '(5A04)' in data_one:
                # 시간
                list_data = data_one.split(' DEBUG ')
                cg_date_time = dt.datetime.strptime(list_data[0], '%Y-%m-%d %H:%M:%S,%f')

                # 응답코드, 거리일시, 승인번호
                list_second_data = list_data[1].split(' : ')[1]
                payment_code = int(list_second_data[50:52], 16)
                # 시간, 타입, 결제요금, 승인번호, 응답코드, 거래일시
                payment_data.append([cg_date_time, 600, None, None, payment_code, None])

    server_columns = ['시간', '카드타입', '카드번호', '서버_전력량(W)', '충전시간(s)', '전압(V)', '전류(A)', 'state']
    wattage_columns = ['시간', '현월_전력량(W)', '전월_전력량(W)', '전전월_전력량(W)']
    volt_columns = ['시간', '전력량계_전압(V)', '전력량계_전류(A)']
    board_columns = ['시간', 'EMG버튼여부', '충전상태', '충전_에러코드', 'SOC(%)', '출력가능_전압(V)', '출력가능_전류(A)', '전압(V)', '전류(A)', '남은시간(s)', '충전코드', 'state']
    payment_columns = ['시간', 'state', '결제금액(원)', '결제승인번호', '응답코드', '결제시간']

    ananytics_name = 'datafile' + '/' + file_name
    makedirs('./' + ananytics_name)

    f, ax = plt.subplots(1, 1, figsize=(20, 10))
    # 서버 카드 결제 데이터
    if server_send_data:
        server_df = pd.DataFrame(server_send_data, columns=server_columns)
        server_df_name = './' + ananytics_name + '/' + file_name + '_Server' + '.csv'
        server_df.to_csv(server_df_name, encoding="utf-8-sig")
        print(server_df_name)

        server_df_100 = server_df.loc[server_df['state'] == 100]
        server_df_300 = server_df.loc[server_df['state'] == 300]
        server_df.plot(x='시간', y='서버_전력량(W)', linestyle='--', marker='o', ax=ax)
        for server_start in server_df_100['시간']:
            plt.axvline(x=server_start, color='r', linestyle='--', linewidth=1)
        for server_end in server_df_300['시간']:
            plt.axvline(x=server_end, color='b', linestyle='--', linewidth=1)
    if wattage_volt_ampere_data:
        volt_ampere_df = pd.DataFrame(wattage_volt_ampere_data, columns=volt_columns)
        volt_ampere_df.plot(x='시간', y='전력량계_전압(V)', marker='o', ax=ax)
        volt_ampere_df.plot(x='시간', y='전력량계_전류(A)', marker='o', ax=ax)
    if payment_data:
        payment_data_df = pd.DataFrame(payment_data, columns=payment_columns)
        payment_data_df_name = './' + ananytics_name + '/' + file_name + '_Payment' + '.csv'
        payment_data_df.to_csv(payment_data_df_name, encoding="utf-8-sig")
        print(payment_data_df_name)

        # 결제
        payment_data_df_payment = payment_data_df.loc[payment_data_df['state'] == 300]
        for payment_ok_time in payment_data_df_payment['시간']:
            plt.axvline(x=payment_ok_time, color='m', linestyle='--', linewidth=2)

        # 부분 취소
        payment_data_df_cancel = payment_data_df.loc[payment_data_df['state'] == 500]
        for payment_ok_time in payment_data_df_cancel['시간']:
            plt.axvline(x=payment_ok_time, color='c', linestyle='--', linewidth=2)

    plt.grid(True)
    server_picture_name = './' + ananytics_name + '/' + file_name + '_Server' + '_fig' + '.png'
    print(server_picture_name)
    plt.rc('axes', unicode_minus=False)
    plt.savefig(server_picture_name)

    # 전력량계 데이터
    f, ax = plt.subplots(1, 1, figsize=(20, 10))
    if wattage_wattage_data:
        wattage_df = pd.DataFrame(wattage_wattage_data, columns=wattage_columns)
        wattage_df_name = './' + ananytics_name + '/' + file_name + '_Wattage' + '.csv'
        wattage_df.to_csv(wattage_df_name, encoding="utf-8-sig")
        print(wattage_df_name)


        wattage_df.plot(x='시간', y='현월_전력량(W)', marker='o', ax=ax)

    plt.grid(True)
    wattage_picture_name = './' + ananytics_name + '/' + file_name + '_Wattage' + '_fig' + '.png'
    print(wattage_picture_name)
    plt.rc('axes', unicode_minus=False)
    plt.savefig(wattage_picture_name)

    # 보드 데이터
    f, ax = plt.subplots(1, 1, figsize=(20, 10))
    if board_receive_data:
        board_receive_data_df = pd.DataFrame(board_receive_data, columns=board_columns)
        board_receive_data_df_name = './' + ananytics_name + '/' + file_name + '_Board' + '.csv'
        board_receive_data_df.to_csv(board_receive_data_df_name, encoding="utf-8-sig")
        print(board_receive_data_df_name)

        board_receive_data_df_8c = board_receive_data_df.loc[board_receive_data_df['state'] == 100]
        # soc 기록
        board_receive_data_df_8c.plot(x='시간', y='SOC(%)', marker='o', ax=ax)

        # 전압 기록
        board_receive_data_df_8c.plot(x='시간', y='전압(V)', marker='o', ax=ax)

        # 전류 기록
        board_receive_data_df_8c.plot(x='시간', y='전류(A)', marker='o', ax=ax)

        # emg 버튼 기록
        board_receive_data_df_8c_emg = board_receive_data_df_8c.loc[board_receive_data_df_8c['EMG버튼여부'] == 50]
        for emg_data_time in board_receive_data_df_8c_emg['시간']:
            plt.axvline(x=emg_data_time, color='r', linestyle='--', linewidth=3)

        # 초기화 되는 시간
        board_receive_data_df_8f = board_receive_data_df.loc[board_receive_data_df['state'] == 200]
        for init_time in board_receive_data_df_8f['시간']:
            plt.axvline(x=init_time, color='b', linestyle='--', linewidth=3)

    plt.grid(True)
    board_picture_name = './' + ananytics_name + '/' + file_name + '_Board' + '_fig' + '.png'
    print(board_picture_name)
    plt.rc('axes', unicode_minus=False)
    plt.savefig(board_picture_name)

# Basic_Path = r'D:\USER\Desktop\Omni_Logs'
# datapathAndanaytics(Basic_Path)

root = Tk()
root.title("로그 데이터를 분석해 봅시다.")
root.geometry("540x300+100+100")
root.resizable(False, False)

def ask():
    root.dirName = filedialog.askdirectory()
    txt.configure(text="pwd: " + root.dirName)


lbl = Label(root, text="주소를 지정하세요")
lbl.pack()

txt = Label(root, text=" ")
txt.pack()

btn = Button(root, text="폴더 주소 지정", command=ask)
btn.pack()

root.dirName = ''
btn1 = Button(root, text="데이터 분석 실행", command=lambda: datapathAndanaytics(root.dirName))
btn1.pack()

root.mainloop()
