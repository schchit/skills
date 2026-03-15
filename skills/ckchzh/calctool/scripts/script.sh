#!/bin/bash
cmd_eval() { local expr="$*"; [ -z "$expr" ] && { echo "Usage: calctool # eval <expression>"; return 1; }
    python3 -c "
import math
expr='$expr'.replace('^','**')
try: print('= {}'.format(eval(expr)))
except Exception as e: print('Error: {}'.format(e))
"; }
cmd_percent() { local val="$1" pct="$2"
    [ -z "$val" ] || [ -z "$pct" ] && { echo "Usage: calctool percent <value> <percent>"; return 1; }
    python3 -c "
v=float('$val'); p=float('$pct')
print('{} of {} = {}'.format('$pct%','$val',v*p/100))
print('{} + {}% = {}'.format('$val','$pct',v+v*p/100))
print('{} - {}% = {}'.format('$val','$pct',v-v*p/100))
"; }
cmd_tip() { local amount="$1" pct="${2:-15}"
    [ -z "$amount" ] && { echo "Usage: calctool tip <amount> [percent]"; return 1; }
    python3 -c "
a=float('$amount'); p=float('$pct')
tip=a*p/100
print('Bill: \${:.2f}'.format(a))
print('Tip ({}%): \${:.2f}'.format(int(p),tip))
print('Total: \${:.2f}'.format(a+tip))
for split in [2,3,4]:
 print('  Split {}: \${:.2f} each'.format(split,(a+tip)/split))
"; }
cmd_loan() { local amount="$1" rate="$2" years="$3"
    [ -z "$amount" ] || [ -z "$rate" ] || [ -z "$years" ] && { echo "Usage: calctool loan <amount> <annual_rate%> <years>"; return 1; }
    python3 -c "
P=float('$amount'); r=float('$rate')/100/12; n=int('$years')*12
if r>0: payment=P*(r*(1+r)**n)/((1+r)**n-1)
else: payment=P/n
total=payment*n
print('Loan Calculator:')
print('  Principal: \${:,.2f}'.format(P))
print('  Rate: {}% annual'.format('$rate'))
print('  Term: {} years ({} months)'.format('$years',n))
print('  Monthly payment: \${:,.2f}'.format(payment))
print('  Total paid: \${:,.2f}'.format(total))
print('  Total interest: \${:,.2f}'.format(total-P))
"; }
cmd_sci() { local fn="$1" val="$2"
    [ -z "$fn" ] || [ -z "$val" ] && { echo "Usage: calctool sci <sqrt|log|sin|cos|tan|exp|abs> <value>"; return 1; }
    python3 -c "
import math
v=float('$val')
fns={'sqrt':math.sqrt,'log':math.log,'log10':math.log10,'sin':math.sin,'cos':math.cos,'tan':math.tan,'exp':math.exp,'abs':abs,'ceil':math.ceil,'floor':math.floor}
fn=fns.get('$fn')
if fn: print('{}({}) = {}'.format('$fn','$val',fn(v)))
else: print('Unknown function. Available: {}'.format(', '.join(fns.keys())))
"; }
cmd_help() { echo "CalcTool - Terminal Calculator"; echo "Commands: # eval <expr> | percent <val> <pct> | tip <amount> [pct] | loan <amt> <rate> <yrs> | sci <func> <val> | help"; }
cmd_info() { echo "CalcTool v1.0.0 | Powered by BytesAgain"; }
case "$1" in eval) shift; cmd_# eval "$@";; percent) shift; cmd_percent "$@";; tip) shift; cmd_tip "$@";; loan) shift; cmd_loan "$@";; sci) shift; cmd_sci "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
