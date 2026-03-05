#!/usr/bin/env python3
"""
Medical Record Processor with SkillPay Billing Integration
Processes unstructured medical notes into standardized EMR format.
"""

import json
import sys
import argparse
import re
import os
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════
# SkillPay Billing Integration / 计费接入
# ═══════════════════════════════════════════════════
BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = os.environ.get('SKILLPAY_API_KEY', '')
SKILL_ID = os.environ.get('SKILLPAY_SKILL_ID', '')  # Set your SkillPay Skill ID
DEFAULT_PRICE = 0.001  # USDT per call


class SkillPayBilling:
    """SkillPay billing integration handler."""
    
    def __init__(self, api_key: str = BILLING_API_KEY, skill_id: str = SKILL_ID):
        self.api_key = api_key
        self.skill_id = skill_id
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make HTTP request to SkillPay API."""
        url = f"{BILLING_API_URL}{endpoint}"
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        
        try:
            if method == 'POST' and data:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers,
                    method=method
                )
            else:
                req = urllib.request.Request(url, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_balance(self, user_id: str) -> float:
        """
        ① Check balance / 查余额 / 残高確認
        Returns USDT balance amount.
        """
        result = self._make_request(f'/api/v1/billing/balance?user_id={user_id}')
        return result.get('balance', 0.0)
    
    def charge_user(self, user_id: str, amount: float = DEFAULT_PRICE) -> Dict[str, Any]:
        """
        ② Charge per call / 每次调用扣费 / 呼び出しごとの課金
        Returns: {ok: bool, balance: float, paymentUrl?: str}
        """
        result = self._make_request('/api/v1/billing/charge', method='POST', data={
            'user_id': user_id,
            'skill_id': self.skill_id,
            'amount': amount,
        })
        
        if result.get('success'):
            return {
                'ok': True,
                'balance': result.get('balance', 0.0),
            }
        else:
            # Insufficient balance → return payment link
            return {
                'ok': False,
                'balance': result.get('balance', 0.0),
                'paymentUrl': result.get('payment_url'),
            }
    
    def get_payment_link(self, user_id: str, amount: float) -> str:
        """
        ③ Generate payment link / 生成充值链接 / 決済リンク生成
        Returns BNB Chain USDT payment link.
        """
        result = self._make_request('/api/v1/billing/payment-link', method='POST', data={
            'user_id': user_id,
            'amount': amount,
        })
        return result.get('payment_url', '')


class MedicalRecordStructurer:
    """Main class for structuring medical records."""
    
    def __init__(self, api_key: str = BILLING_API_KEY):
        self.billing = SkillPayBilling(api_key)
        self.fields = {
            "patient_name": None,
            "gender": None,
            "age": None,
            "chief_complaint": None,
            "history_present_illness": None,
            "past_medical_history": None,
            "physical_examination": None,
            "diagnosis": None,
            "treatment_plan": None,
            "medications": None,
            "follow_up": None,
            "doctor_name": None,
            "record_date": None
        }
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient demographics from text."""
        info = {}
        
        # Extract name (支持中文和英文)
        name_patterns = [
            r'患者[：:]?\s*([\u4e00-\u9fa5]{2,4})',
            r'姓名[：:]?\s*([\u4e00-\u9fa5]{2,4})',
            r'([\u4e00-\u9fa5]{2,4})[，,]\s*(?:男|女)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                info['patient_name'] = match.group(1)
                break
        
        # Extract gender
        if '男' in text:
            info['gender'] = '男'
        elif '女' in text:
            info['gender'] = '女'
        elif 'male' in text.lower():
            info['gender'] = 'Male'
        elif 'female' in text.lower():
            info['gender'] = 'Female'
        
        # Extract age
        age_patterns = [
            r'(\d+)[\s]*岁',
            r'年龄[：:]?\s*(\d+)',
            r'(\d+)[\s]*years?\s*old',
            r'age[\s:]+(\d+)',
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['age'] = int(match.group(1))
                break
        
        return info
    
    def extract_medical_fields(self, text: str) -> Dict[str, Any]:
        """Extract medical information fields."""
        fields = {}
        
        # Chief complaint / 主诉
        cc_patterns = [
            r'主诉[：:]?\s*([^。\n]+)',
            r'chief complaint[：:]?\s*([^。\n]+)',
            r'(?:主诉|complaint)[：:]?\s*([^。\n]{3,50})',
        ]
        for pattern in cc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['chief_complaint'] = match.group(1).strip()
                break
        
        # Diagnosis / 诊断
        dx_patterns = [
            r'诊断[：:]?\s*([^。\n]+)',
            r'初步诊断[：:]?\s*([^。\n]+)',
            r'diagnosis[：:]?\s*([^。\n]+)',
        ]
        for pattern in dx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['diagnosis'] = match.group(1).strip()
                break
        
        # Treatment plan / 治疗方案
        tx_patterns = [
            r'(?:治疗|处理|方案)[：:]?\s*([^。\n]+)',
            r'治疗计划[：:]?\s*([^。\n]+)',
            r'treatment[：:]?\s*([^。\n]+)',
        ]
        for pattern in tx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['treatment_plan'] = match.group(1).strip()
                break
        
        # Medications / 药物
        med_patterns = [
            r'(?:药物|用药|处方)[：:]?\s*([^。\n]+)',
            r'(?:开|给予)[：:]?\s*([^。\n]+?)(?:口服|注射|外用)',
            r'medication[：:]?\s*([^。\n]+)',
        ]
        for pattern in med_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['medications'] = match.group(1).strip()
                break
        
        # Physical examination / 体格检查
        pe_patterns = [
            r'(?:体格检查|查体|体检)[：:]?\s*([^。\n]+)',
            r'physical examination[：:]?\s*([^。\n]+)',
        ]
        for pattern in pe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['physical_examination'] = match.group(1).strip()
                break
        
        # History / 病史
        hx_patterns = [
            r'(?:现病史|病史)[：:]?\s*([^。\n]+)',
            r'history of present illness[：:]?\s*([^。\n]+)',
        ]
        for pattern in hx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['history_present_illness'] = match.group(1).strip()
                break
        
        return fields
    
    def structure_record(self, text: str) -> Dict[str, Any]:
        """
        Main method to structure a medical record.
        Returns standardized EMR format.
        """
        # Extract all information
        patient_info = self.extract_patient_info(text)
        medical_fields = self.extract_medical_fields(text)
        
        # Merge into standard format
        structured = {
            "emr_version": "1.0",
            "record_id": f"EMR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "record_date": datetime.now().isoformat(),
            "patient_demographics": {
                "name": patient_info.get('patient_name', 'Unknown'),
                "gender": patient_info.get('gender', 'Unknown'),
                "age": patient_info.get('age', None),
            },
            "clinical_information": {
                "chief_complaint": medical_fields.get('chief_complaint', ''),
                "history_of_present_illness": medical_fields.get('history_present_illness', ''),
                "past_medical_history": medical_fields.get('past_medical_history', ''),
                "physical_examination": medical_fields.get('physical_examination', ''),
            },
            "assessment_and_plan": {
                "diagnosis": medical_fields.get('diagnosis', ''),
                "treatment_plan": medical_fields.get('treatment_plan', ''),
                "medications": medical_fields.get('medications', ''),
                "follow_up_instructions": medical_fields.get('follow_up', ''),
            },
            "metadata": {
                "source_text": text,
                "processed_at": datetime.now().isoformat(),
                "processor_version": "1.0.1"
            }
        }
        
        return structured
    
    def process(self, text: str, user_id: str = "") -> Dict[str, Any]:
        """
        Full processing pipeline with SkillPay billing.
        """
        if not user_id:
            return {
                "success": False,
                "error": "User ID is required for billing"
            }
        
        # Step 1: Check balance first
        balance = self.billing.check_balance(user_id)
        if balance < DEFAULT_PRICE:
            payment_url = self.billing.get_payment_link(user_id, DEFAULT_PRICE)
            return {
                "success": False,
                "error": "Insufficient balance",
                "balance": balance,
                "paymentUrl": payment_url,
            }
        
        # Step 2: Charge user
        charge_result = self.billing.charge_user(user_id, DEFAULT_PRICE)
        
        if not charge_result.get('ok'):
            return {
                "success": False,
                "error": "Payment failed",
                "balance": charge_result.get('balance', 0),
                "paymentUrl": charge_result.get('paymentUrl'),
            }
        
        # Step 3: Structure the record
        structured_record = self.structure_record(text)
        
        return {
            "success": True,
            "balance": charge_result.get('balance'),
            "structured_record": structured_record
        }


def process_medical_record(input_text: str, user_id: str = "", api_key: str = BILLING_API_KEY) -> Dict[str, Any]:
    """
    Convenience function for processing medical records.
    """
    processor = MedicalRecordStructurer(api_key)
    return processor.process(input_text, user_id)


def main():
    parser = argparse.ArgumentParser(description='Medical Record Structurer')
    parser.add_argument('--input', '-i', required=True, help='Input medical record text')
    parser.add_argument('--user-id', '-u', required=True, help='User ID for billing')
    parser.add_argument('--api-key', '-k', default=BILLING_API_KEY, help='SkillPay API key')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Use environment variable if not provided
    api_key = args.api_key or os.environ.get('SKILLPAY_API_KEY', '')
    
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "API key is required. Set SKILLPAY_API_KEY environment variable or use --api-key"
        }, ensure_ascii=False))
        return 1
    
    # Process the record
    result = process_medical_record(args.input, args.user_id, api_key)
    
    # Output result
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Result saved to: {args.output}")
    else:
        print(output_json)
    
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
