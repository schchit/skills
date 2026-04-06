/**
 * 统一 CLI 参数解析器
 *
 * 所有 5GC 脚本均使用此解析器，保证参数格式一致。
 *
 * 标准格式:
 *   ADD:  node <script> --name <名称> --project <工程> [--field <值> ...]
 *   EDIT: node <script> --name <名称> --project <工程> --set-<field> <value>
 *       node <script> --id <ID> --set-<field> <value>
 *       node <script> --project <工程> --set-<field> <value>    (批量)
 *
 * 用法: const args = parseArgs(); → { name, project, id, sets, headed, url }
 */

const URL_RE = /^--url$/i;
const PROJECT_RE = /^--project$|^--project$/i;
const NAME_RE = /^--name$/i;
const ID_RE = /^--id$/i;
const HEADED_RE = /^--headed$/i;
const SET_RE = /^--set-/;

function parseArgs(argv) {
  const args = argv || process.argv.slice(2);
  const result = {
    name: null,
    project: 'XW_S5GC_1',        // 默认工程
    id: null,
    sets: {},
    headed: false,
    url: 'https://192.168.3.89',
    _positional: []              // 保留位置参数兼容
  };

  for (let i = 0; i < args.length; i++) {
    const a = args[i];

    // 统一转小写匹配（处理 --Name, --NAME 等）
    const al = a.toLowerCase();

    if (URL_RE.test(a)) {
      let u = args[++i];
      if (u && !u.startsWith('http')) u = 'https://' + u;
      result.url = u || result.url;
    } else if (PROJECT_RE.test(a) || al === '-p') {
      result.project = args[++i] || result.project;
    } else if (NAME_RE.test(a) || al === '-n') {
      result.name = args[++i] || result.name;
    } else if (ID_RE.test(a)) {
      result.id = args[++i] || result.id;
    } else if (HEADED_RE.test(a) || al === '--head' || al === '-h' && args[i + 1] === undefined) {
      result.headed = true;
    } else if (SET_RE.test(a)) {
      const key = a.substring(5).replace(/-/g, '_'); // --set-msisdn → msisdn
      result.sets[key] = args[++i];
    } else if (a.startsWith('--')) {
      // 其他 --field value 形式（非 --set-）
      const key = a.substring(2).replace(/-/g, '_');
      result.sets[key] = args[++i];
    } else if (!a.startsWith('-')) {
      // 纯位置参数（非选项）：视为 name
      if (!result.name) result.name = a;
      else result._positional.push(a);
    }
    // 忽略单独出现的 -h（它是 --headed 的缩写，但后面没值时才有意义）
  }

  return result;
}

/**
 * 统一打印帮助信息
 */
function printHelp(additionalFields = []) {
  console.log(`
用法: node <script> --name <名称> --project <工程> [--set-<字段> <值>] [--headed]

参数:
  --name <名称>       网元名称（ADD/EDIT 时使用）
  --project <工程>     目标工程（默认: XW_S5GC_1）
  --id <ID>           直接指定网元 ID（EDIT 时使用）
  --set-<字段> <值>   修改指定字段的值（EDIT 时使用）
  --url <地址>         5GC 仪表地址（默认: https://192.168.3.89）
  --headed            以有头模式运行（显示浏览器窗口）

示例:
  # 添加
  node <script> --name MyAMF --project XW_S5GC_1 --mcc 460 --mnc 01
  node <script> --name MyGNB --project XW_S5GC_1 --count 1 --mcc 460 --mnc 01 --stac 1 --etac 100

  # 编辑（单个）
  node <script> --id 12345 --set-sbi_ip 10.0.0.1
  node <script> --name MyAMF --project XW_S5GC_1 --set-sbi_ip 10.0.0.1

  # 批量编辑
  node <script> --project XW_S5GC_1 --set-replay_ip 10.0.0.1

可编辑字段:${additionalFields.map(f => '\n  ' + f).join('')}
`);
}

// 暴露
module.exports = { parseArgs, printHelp };
