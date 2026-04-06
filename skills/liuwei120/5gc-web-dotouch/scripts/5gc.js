/**
 * 5GC Web 仪表统一 CLI
 *
 * 用法: node 5gc.js <entity> <action> [options]
 *
 * entity (网元类型):  amf | udm | smf | upf | gnb | ue | pcf | nrf
 * action (操作类型):  add | edit
 *
 * 通用选项:
 *   --url <地址>       5GC 仪表地址（默认 https://192.168.3.89）
 *   --project <工程>   目标工程名称
 *   --name <名称>      网元名称（用于单条记录筛选）
 *   --id <id>         网元 ID（直接编辑指定 ID）
 *   --headed          以有头模式运行（显示浏览器窗口）
 *
 * 字段修改（edit 模式）--set-<field> <value>:
 *   AMF:  name|sbi_ip|sbi_port|amf_name|guami|mcc|mnc|sst|sd|ap1|ap2|ap3|ap4|ap5
 *   UDM:  name|auth_supi|auth_op_type|op_opc|aud_method|scheme|id|priority
 *   SMF:  name|pfcp_ip|n3_ip|n6_ip|dnn|snssai|sliceamba_type
 *   UPF:  name|n4_ip|n3_ip|n6_ip|dnn|snssai|count|static_arp|ue_ip_pool
 *   GNB:  name|ngap_ip|user_sip_ip_v4|mcc|mnc|stac|etac|node_id|cell_count|replay_ip|replay_port
 *   UE:   name|count|mcc|mnc|s_imsi|key|opc|imeisv|msisdn|user_sip_ip_v4|user_sip_ip_v6|replay_ip|replay_port
 *
 * 示例:
 *   node 5gc.js amf add   --name AMF_TEST --project XW_S5GC_1 --sbi-ip 10.0.0.1
 *   node 5gc.js gnb add   --name GNB_TEST --project XW_S5GC_1 --count 1 --mcc 460 --mnc 01 --stac 1 --etac 100
 *   node 5gc.js ue add    --name UE_001 --imsi 460001234567890 --msisdn 8613888888888
 *   node 5gc.js ue edit   --project XW_S5GC_1 --set-msisdn 8613888888888
 *   node 5gc.js ue edit   --id 10337 --set-msisdn 8613888888888
 *   node 5gc.js gnb edit  --project XW_S5GC_1 --set-user_sip_ip_v4 200.200.200.200
 *   node 5gc.js upf edit  --project XW_S5GC_1 --set-n4_ip 10.0.0.5
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const SCRIPTS_DIR = __dirname;

const argv = process.argv.slice(2);

if (argv.length === 0 || argv[0] === '--help' || argv[0] === '-h') {
  printHelp();
  process.exit(0);
}

const entity = argv[0].toLowerCase();
const action = (argv[1] || '').toLowerCase();

const VALID_ENTITIES = ['amf', 'udm', 'smf', 'upf', 'gnb', 'ue', 'pcf', 'nrf'];
const VALID_ACTIONS = ['add', 'edit'];

if (!VALID_ENTITIES.includes(entity)) {
  console.error(`\n❌ 未知网元类型: ${entity}`);
  console.error('   可用: ' + VALID_ENTITIES.join(', '));
  process.exit(1);
}
if (!action || !VALID_ACTIONS.includes(action)) {
  console.error(`\n❌ 未知操作: ${action || '(空)'}`);
  console.error('   用法: node 5gc.js <entity> <action> [options]');
  console.error('   示例: node 5gc.js amf add --help');
  process.exit(1);
}

// 子脚本映射
// 所有 edit 均映射到 edit 脚本（单条 + 批量二合一）
const scriptMap = {
  'amf:add':   'amf-add-skill.js',
  'amf:edit':  'amf-edit-skill.js',
  'udm:add':   'ausf-udm-add-skill.js',
  'udm:edit':  'ausf-udm-edit-skill.js',
  'smf:add':   'smf-pgwc-add-skill.js',
  'smf:edit':  'smf-pgwc-edit-skill.js',
  'upf:add':   'upf-add-skill.js',
  'upf:edit':  'upf-edit-skill.js',
  'gnb:add':   'gnb-add-skill.js',
  'gnb:edit':  'gnb-edit-skill.js',
  'ue:add':    'ue-add-skill.js',
  'ue:edit':   'ue-edit-skill.js',
  'pcf:add':   'pcf-add-skill.js',
  'pcf:edit':  'pcf-edit-skill.js',
  'nrf:add':   'nrf-add-skill.js',
  'nrf:edit':  'nrf-edit-skill.js',
};

const scriptFile = scriptMap[`${entity}:${action}`];
const scriptPath = path.join(SCRIPTS_DIR, scriptFile);

if (!fs.existsSync(scriptPath)) {
  console.error(`\n❌ 脚本不存在: ${scriptPath}`);
  process.exit(1);
}

// 去掉 entity 和 action 后的参数传给子脚本
const childArgv = argv.slice(2);

console.log(`\n▶ 5GC ${entity.toUpperCase()} ${action}`);
console.log('  → node ' + scriptFile + ' ' + childArgv.join(' ') + '\n');

// 用子进程调用，保持 CLI 参数隔离
const child = spawn('node', [scriptPath, ...childArgv], {
  stdio: 'inherit',
  shell: true,
  cwd: SCRIPTS_DIR,
});

child.on('exit', (code) => process.exit(code || 0));
child.on('error', (err) => { console.error('启动失败:', err.message); process.exit(1); });

function printHelp() {
  console.log(`
5GC Web 仪表自动化 - 统一 CLI
=============================

用法:
  node 5gc.js <entity> <action> [options]

网元类型 (entity):
  amf   - AMF（接入与移动性管理功能）
  udm   - UDM/AUSF（统一数据管理/认证服务器功能）
  smf   - SMF/PGW-C（会话管理功能/PDN 连接网关控制面）
  upf   - UPF/PGW-U（用户面功能/PDN 连接网关用户面）
  gnb   - gNodeB（5G 基站）
  ue    - UE（用户终端）
  pcf   - PCF/PCRF（策略控制功能）
  nrf   - NRF（网络存储功能）

操作 (action):
  add   - 添加网元实例
  edit  - 编辑网元（单个或批量）

通用选项:
  --url <地址>        5GC 仪表地址（默认 https://192.168.3.89）
  --project <工程>    目标工程名称
  --name <名称>       网元名称
  --id <id>          网元 ID（edit 模式）
  --headed           以有头模式运行（显示浏览器）
  --help             显示本帮助

字段修改（edit 模式 --set-<field> <value>）:
  AMF:  name|sbi_ip|sbi_port|amf_name|guami|mcc|mnc|sst|sd|ap1|ap2|ap3|ap4|ap5
  UDM:  name|auth_supi|auth_op_type|op_opc|aud_method|scheme|id|priority
  SMF:  name|pfcp_ip|n3_ip|n6_ip|dnn|snssai|sliceamba_type
  UPF:  name|n4_ip|n3_ip|n6_ip|dnn|snssai|count|static_arp|ue_ip_pool
  GNB:  name|ngap_ip|user_sip_ip_v4|mcc|mnc|stac|etac|node_id|cell_count|replay_ip|replay_port
  \n  PCF:  http2_sip|http2_port|mcc|mnc

添加示例:
  node 5gc.js amf  add --name AMF_TEST --project XW_S5GC_1 --sbi-ip 10.0.0.1 --mcc 460 --mnc 01
  node 5gc.js gnb  add --name GNB_TEST --project XW_S5GC_1 --count 1 --mcc 460 --mnc 01 --stac 1 --etac 100
  node 5gc.js ue   add --name UE_001 --imsi 460001234567890 --msisdn 8613888888888
  node 5gc.js smf  add --name SMF_TEST --project XW_S5GC_1 --pfcp-ip 10.0.0.2
  node 5gc.js upf  add --name UPF_TEST --project XW_S5GC_1 --n4-ip 10.0.0.3

编辑示例:
  node 5gc.js ue   edit --project XW_S5GC_1 --set-msisdn 8613888888888
  node 5gc.js ue   edit --id 10337 --set-msisdn 8613888888888
  node 5gc.js gnb  edit --project XW_S5GC_1 --set-user_sip_ip_v4 200.200.200.200
  node 5gc.js upf  edit --project XW_S5GC_1 --set-n4_ip 10.0.0.5
`);
}
