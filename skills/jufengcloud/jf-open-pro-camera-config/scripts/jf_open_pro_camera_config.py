#!/usr/bin/env python3
"""
JF 杰峰摄像机配置工具 - Python 版本

仅支持环境变量配置凭据，避免命令行泄露风险。

用法:
    export JF_UUID="your-uuid"
    export JF_APPKEY="your-appkey"
    export JF_APPSECRET="your-appsecret"
    export JF_MOVECARD=5
    export JF_SN="your-device-sn"
    
    python jf_open_pro_camera_config.py motion-detect --action get
    python jf_open_pro_camera_config.py motion-detect --action set --enable true --level 3
    python jf_open_pro_camera_config.py human-detection --action set --enable true --sensitivity 2
    python jf_open_pro_camera_config.py human-track --action set --enable true --sensitivity 1 --return-time 10
"""

import argparse
import hashlib
import json
import os
import time
import urllib.request
import urllib.error


def str2byte(s):
    return list(s.encode('utf-8'))


def change(encrypt_str, move_card):
    encrypt_byte = str2byte(encrypt_str)
    length = len(encrypt_byte)
    for idx in range(length):
        tmp = encrypt_byte[idx] if (idx % move_card) > ((length - idx) % move_card) else encrypt_byte[length - (idx + 1)]
        encrypt_byte[idx], encrypt_byte[length - (idx + 1)] = encrypt_byte[length - (idx + 1)], tmp
    return encrypt_byte


def merge_byte(encrypt_byte, change_byte):
    length = len(encrypt_byte)
    temp = [0] * (length * 2)
    for idx in range(length):
        temp[idx] = encrypt_byte[idx]
        temp[length * 2 - 1 - idx] = change_byte[idx]
    return temp


def get_signature(uuid, app_key, app_secret, time_millis, move_card=5):
    encrypt_str = uuid + app_key + app_secret + time_millis
    encrypt_byte = str2byte(encrypt_str)
    change_byte = change(encrypt_str, move_card)
    merged_byte = merge_byte(encrypt_byte, change_byte)
    return hashlib.md5(bytes(merged_byte)).hexdigest()


def get_time_millis():
    return str(int(time.time() * 1000)).zfill(20)


def generate_request_id():
    import random
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))


def https_post(url, data, headers):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise Exception(f'HTTP 错误：{e.code} - {e.reason}')
    except urllib.error.URLError as e:
        raise Exception(f'请求失败：{e.reason}')


def get_device_token(config):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/token"
    headers = {
        'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis,
        'signature': signature, 'X-Request-Id': generate_request_id()
    }
    data = {'sns': [config['deviceSn']], 'accessToken': ''}
    response = https_post(url, data, headers)
    
    if response.get('code') != 2000:
        raise Exception(f"获取 Token 失败：{response.get('msg')}")
    if not response.get('data') or len(response['data']) == 0:
        raise Exception('获取 Token 失败：返回数据为空')
    return response['data'][0]['token']


def get_motion_detect_config(config, device_token, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/getconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    data = {'Name': 'Detect.MotionDetect'}
    if channel > 0:
        data['Channel'] = str(channel)
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"获取移动侦测配置失败：{response.get('msg')}")
    return response['data']


def set_motion_detect_config(config, device_token, enable, level=3, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/setconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    
    data = {
        'Name': 'Detect.MotionDetect',
        'Detect.MotionDetect': [{
            'AlarmType': 0, 'Enable': enable, 'Level': level,
            'Region': ['0xFFFFFFFF'] * 32,
            'PIRCheckTime': 0, 'PirSensitive': 0,
            'PirTimeSection': {'PirTimeSectionOne': {'Enable': False, 'WeekMask': 0}, 'PirTimeSectionTwo': {'Enable': False, 'WeekMask': 0}},
            'EventHandler': {
                'AlarmInfo': '', 'AlarmOutEnable': False, 'AlarmOutLatch': 10, 'AlarmOutMask': '0x00000000',
                'BeepEnable': False, 'Dejitter': 0, 'EventLatch': 2, 'FTPEnable': False, 'LogEnable': False,
                'MailEnable': False, 'MatrixEnable': False, 'MatrixMask': '0x00000000', 'MessageEnable': True,
                'MsgtoNetEnable': False, 'PtzEnable': True, 'PtzLink': [['None', 0] for _ in range(64)],
                'RecordEnable': True, 'RecordLatch': 30, 'RecordMask': '0x00000001', 'SnapEnable': True,
                'SnapShotMask': '0x00000001',
                'TimeSection': [['1 00:00:00-24:00:00'] + ['0 00:00:00-24:00:00'] * 5 for _ in range(7)],
                'TipEnable': False, 'TourEnable': False, 'TourMask': '0x00000000', 'VoiceEnable': False, 'VoiceType': 520
            }
        }]
    }
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"设置移动侦测配置失败：{response.get('msg')}")
    return response['data']


def get_human_detection_config(config, device_token, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/getconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    data = {'Name': 'Detect.HumanDetection'}
    if channel > 0:
        data['Channel'] = str(channel)
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"获取人形检测配置失败：{response.get('msg')}")
    return response['data']


def set_human_detection_config(config, device_token, enable, sensitivity=1, object_type=0, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/setconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    
    data = {
        'Name': 'Detect.HumanDetection',
        'Detect.HumanDetection': [{
            'Enable': enable, 'ObjectType': object_type, 'PedFdrAlg': 0, 'AlgoCreate': True,
            'ShowRule': False, 'ShowTrack': False, 'Sensitivity': sensitivity, 'PushInterval': 3000,
            'PedRule': [
                {'Enable': False, 'RuleType': 1, 'RuleLine': {'AlarmDirect': 2, 'Pts': {'StartX': 100, 'StartY': 100, 'StopX': 8191, 'StopY': 8191}}, 'RuleRegion': {'AlarmDirect': 2, 'PtsNum': 4, 'Pts': [{'X': 100, 'Y': 100}, {'X': 8191, 'Y': 100}, {'X': 8191, 'Y': 8191}, {'X': 100, 'Y': 8191}]}},
                {'Enable': False, 'RuleType': 1, 'RuleLine': {'AlarmDirect': 2, 'Pts': {'StartX': 100, 'StartY': 100, 'StopX': 8191, 'StopY': 8191}}, 'RuleRegion': {'AlarmDirect': 2, 'PtsNum': 4, 'Pts': [{'X': 100, 'Y': 100}, {'X': 8191, 'Y': 100}, {'X': 8191, 'Y': 8191}, {'X': 100, 'Y': 8191}]}},
                {'Enable': False, 'RuleType': 1, 'RuleLine': {'AlarmDirect': 2, 'Pts': {'StartX': 100, 'StartY': 100, 'StopX': 8191, 'StopY': 8191}}, 'RuleRegion': {'AlarmDirect': 2, 'PtsNum': 4, 'Pts': [{'X': 100, 'Y': 100}, {'X': 8191, 'Y': 100}, {'X': 8191, 'Y': 8191}, {'X': 100, 'Y': 8191}]}},
                {'Enable': False, 'RuleType': 1, 'RuleLine': {'AlarmDirect': 2, 'Pts': {'StartX': 100, 'StartY': 100, 'StopX': 8191, 'StopY': 8191}}, 'RuleRegion': {'AlarmDirect': 2, 'PtsNum': 4, 'Pts': [{'X': 100, 'Y': 100}, {'X': 8191, 'Y': 100}, {'X': 8191, 'Y': 8191}, {'X': 100, 'Y': 8191}]}}
            ]
        }]
    }
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"设置人形检测配置失败：{response.get('msg')}")
    return response['data']


def get_human_track_config(config, device_token, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/getconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    data = {'Name': 'Detect.DetectTrack'}
    if channel > 0:
        data['Channel'] = str(channel)
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"获取人形追踪配置失败：{response.get('msg')}")
    return response['data']


def set_human_track_config(config, device_token, enable, sensitivity=1, return_time=10, channel=0):
    time_millis = get_time_millis()
    signature = get_signature(config['uuid'], config['appKey'], config['appSecret'], time_millis, config['moveCard'])
    url = f"https://{config['endpoint']}/gwp/v3/rtc/device/setconfig/{device_token}"
    headers = {'uuid': config['uuid'], 'appKey': config['appKey'], 'timeMillis': time_millis, 'signature': signature, 'X-Request-Id': generate_request_id()}
    
    data = {
        'Name': 'Detect.DetectTrack',
        'Detect.DetectTrack': {
            'Enable': 1 if enable else 0,
            'Sensitivity': sensitivity,
            'ReturnTime': return_time
        }
    }
    response = https_post(url, data, headers)
    if response.get('code') != 2000:
        raise Exception(f"设置人形追踪配置失败：{response.get('msg')}")
    return response['data']


def parse_args():
    parser = argparse.ArgumentParser(
        description='JLink 杰峰摄像机配置工具 - Python 版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
环境变量:
  JF_UUID       开放平台用户唯一标识 (必需)
  JF_APPKEY     开放平台应用 Key (必需)
  JF_APPSECRET  开放平台应用密钥 (必需)
  JF_MOVECARD   签名算法偏移量，通常设为 5 (必需)
  JF_SN         设备序列号 (必需)
  JF_ENDPOINT   API 端点，默认 api.jftechws.com (可选)
  JF_CHANNEL    通道号，默认 0 (可选)

示例:
  # 设置环境变量
  export JF_UUID="your-uuid"
  export JF_APPKEY="your-appkey"
  export JF_APPSECRET="your-appsecret"
  export JF_MOVECARD=5
  export JF_SN="your-device-sn"
  
  # 移动侦测 - 获取配置
  python jf_open_pro_camera_config.py motion-detect --action get
  
  # 移动侦测 - 开启（灵敏度 3）
  python jf_open_pro_camera_config.py motion-detect --action set --enable true --level 3
  
  # 人形检测 - 开启（灵敏度 2）
  python jf_open_pro_camera_config.py human-detection --action set --enable true --sensitivity 2
  
  # 人形追踪 - 开启（灵敏度 1，10 秒回位）
  python jf_open_pro_camera_config.py human-track --action set --enable true --sensitivity 1 --return-time 10
        ''')
    
    parser.add_argument('command', choices=['motion-detect', 'human-detection', 'human-track'], help='命令')
    parser.add_argument('--action', choices=['get', 'set'], required=True, help='操作类型')
    parser.add_argument('--enable', type=str, help='开启/关闭 (true/false)')
    parser.add_argument('--level', type=int, help='移动侦测灵敏度 (1-6)')
    parser.add_argument('--sensitivity', type=int, help='人形检测/追踪灵敏度')
    parser.add_argument('--object-type', dest='object_type', type=int, help='检测目标类型 (0:人，1:物体)')
    parser.add_argument('--return-time', dest='return_time', type=int, help='人形追踪回位时间 (秒)')
    
    return parser.parse_args()


def get_config_from_env():
    """从环境变量读取配置"""
    required_vars = ['JF_UUID', 'JF_APPKEY', 'JF_APPSECRET', 'JF_MOVECARD', 'JF_SN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise Exception(f"缺少必需的环境变量：{', '.join(missing_vars)}\n"
                       f"请设置：export JF_UUID='...' JF_APPKEY='...' JF_APPSECRET='...' JF_MOVECARD=5 JF_SN='...'")
    
    return {
        'uuid': os.environ.get('JF_UUID'),
        'appKey': os.environ.get('JF_APPKEY'),
        'appSecret': os.environ.get('JF_APPSECRET'),
        'moveCard': int(os.environ.get('JF_MOVECARD', 5)),
        'endpoint': os.environ.get('JF_ENDPOINT', 'api.jftechws.com'),
        'deviceSn': os.environ.get('JF_SN'),
        'channel': int(os.environ.get('JF_CHANNEL', 0))
    }


def get_motion_level_text(level):
    texts = ['', '最低', '较低', '中', '较高', '很高', '最高']
    return texts[level] if 1 <= level <= 6 else '未知'


def get_human_sensitivity_text(sensitivity):
    texts = ['低', '中', '高', '数量']
    return texts[sensitivity] if 0 <= sensitivity <= 3 else '未知'


def get_ped_fdr_alg_text(alg):
    texts = ['单人形检测', '人形 + 人脸检测', '人形 + 人脸识别', '人形 + 车形检测', '人形 + 车形 + 人脸检测', '宠物']
    return texts[alg] if 0 <= alg <= 5 else '未知'


def main():
    args = parse_args()
    
    try:
        config = get_config_from_env()
    except Exception as e:
        print(f'❌ 配置错误：{e}')
        return 1
    
    try:
        print('========================================')
        title_map = {'motion-detect': '移动侦测', 'human-detection': '人形检测', 'human-track': '人形追踪'}
        print(f"JLink {title_map.get(args.command, '')}配置")
        print('========================================')
        print(f"设备 SN: {config['deviceSn']}")
        print(f"通道号：{config['channel']}")
        print(f"操作：{args.action}")
        print()
        
        device_token = get_device_token(config)
        
        if args.command == 'motion-detect':
            if args.action == 'get':
                result = get_motion_detect_config(config, device_token, config['channel'])
                motion_config = result.get('Detect.MotionDetect', [{}])[0]
                if motion_config:
                    print('=== 移动侦测配置 ===')
                    print(f"开关状态：{'开启 (布防)' if motion_config.get('Enable') else '关闭 (撤防)'}")
                    print(f"灵敏度：{motion_config.get('Level')} ({get_motion_level_text(motion_config.get('Level', 0))})")
            else:
                if args.enable is None:
                    print('❌ 设置操作需要 --enable 参数')
                    return 1
                enable = args.enable.lower() == 'true'
                level = args.level if args.level is not None else 3
                if level < 1 or level > 6:
                    print('❌ 灵敏度必须在 1-6 之间')
                    return 1
                result = set_motion_detect_config(config, device_token, enable, level, config['channel'])
                print(f"✅ 移动侦测{'开启 (布防)' if enable else '关闭 (撤防)'}成功")
                print(f"灵敏度：{level}")
                print(f"返回码：{result.get('Ret')}")
        
        elif args.command == 'human-detection':
            if args.action == 'get':
                result = get_human_detection_config(config, device_token, config['channel'])
                human_config = result.get('Detect.HumanDetection', [{}])[0]
                if human_config:
                    print('=== 人形检测配置 ===')
                    print(f"开关状态：{'开启' if human_config.get('Enable') else '关闭'}")
                    print(f"灵敏度：{human_config.get('Sensitivity')} ({get_human_sensitivity_text(human_config.get('Sensitivity', 0))})")
                    print(f"检测类型：{'人' if human_config.get('ObjectType') == 0 else '物体'}")
                    print(f"算法类型：{get_ped_fdr_alg_text(human_config.get('PedFdrAlg', 0))}")
            else:
                if args.enable is None:
                    print('❌ 设置操作需要 --enable 参数')
                    return 1
                enable = args.enable.lower() == 'true'
                sensitivity = args.sensitivity if args.sensitivity is not None else 1
                object_type = args.object_type if args.object_type is not None else 0
                if sensitivity < 0 or sensitivity > 3:
                    print('❌ 灵敏度必须在 0-3 之间')
                    return 1
                result = set_human_detection_config(config, device_token, enable, sensitivity, object_type, config['channel'])
                print(f"✅ 人形检测{'开启' if enable else '关闭'}成功")
                print(f"灵敏度：{sensitivity}")
                print(f"检测类型：{'人' if object_type == 0 else '物体'}")
                print(f"返回码：{result.get('Ret')}")
        
        elif args.command == 'human-track':
            if args.action == 'get':
                result = get_human_track_config(config, device_token, config['channel'])
                track_config = result.get('Detect.DetectTrack', {})
                if track_config:
                    print('=== 人形追踪配置 ===')
                    print(f"开关状态：{'开启' if track_config.get('Enable') == 1 else '关闭'}")
                    print(f"灵敏度：{track_config.get('Sensitivity')} ({get_human_sensitivity_text(track_config.get('Sensitivity', 0))})")
                    return_time = track_config.get('ReturnTime', 0)
                    print(f"回位时间：{return_time}秒{' (不返回)' if return_time == 0 else ''}")
            else:
                if args.enable is None:
                    print('❌ 设置操作需要 --enable 参数')
                    return 1
                enable = args.enable.lower() == 'true'
                sensitivity = args.sensitivity if args.sensitivity is not None else 1
                return_time = args.return_time if args.return_time is not None else 10
                if sensitivity < 0 or sensitivity > 2:
                    print('❌ 追踪灵敏度必须在 0-2 之间')
                    return 1
                if return_time < 0 or return_time > 600:
                    print('❌ 回位时间必须在 0-600 秒之间')
                    return 1
                result = set_human_track_config(config, device_token, enable, sensitivity, return_time, config['channel'])
                print(f"✅ 人形追踪{'开启' if enable else '关闭'}成功")
                print(f"灵敏度：{sensitivity}")
                print(f"回位时间：{return_time}秒")
                print(f"返回码：{result.get('Ret')}")
        
        print('========================================')
        return 0
    
    except Exception as e:
        print(f'❌ 错误：{e}')
        return 1


if __name__ == '__main__':
    exit(main())
