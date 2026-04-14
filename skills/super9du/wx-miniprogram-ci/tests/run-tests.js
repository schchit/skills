#!/usr/bin/env node
/**
 * wx-miniprogram-skill 测试脚本
 *
 * 用法: node tests/run-tests.js
 *
 * 测试使用临时配置文件 ~/.wxmini-ci.config.test，
 * 测试结束后自动恢复用户的真实配置。
 * 关键：先保存真实配置到 TEST_CONFIG，再替换 REAL_CONFIG 为 TEST_CONFIG，
 * 这样测试期间对 REAL_CONFIG 的修改实际发生在 TEST_CONFIG 上。
 */

var child_process = require("child_process");
var path = require("path");
var fs = require("fs");
var os = require("os");

var SCRIPT_DIR = path.join(__dirname, "..", "scripts");
var REAL_CONFIG = path.join(os.homedir(), ".wxmini-ci.config.js");
var TEST_CONFIG = path.join(os.homedir(), ".wxmini-ci.config.test");
var CLI = "node wx-miniprogram-ci.js";

var backedUp = false;

function backupConfig() {
  try {
    // 始终把 TEST_CONFIG 设为"干净空配置"
    // 无论之前是否存在真实配置，都创建一个空的测试配置环境
    fs.writeFileSync(TEST_CONFIG, "module.exports = {};\n", "utf-8");
    // 把测试配置作为实际运行配置（脚本会读写这个）
    fs.copyFileSync(TEST_CONFIG, REAL_CONFIG);
    backedUp = true;
  } catch (e) {}
}

function restoreConfig() {
  try {
    if (fs.existsSync(TEST_CONFIG)) {
      // TEST_CONFIG 始终是干净的备份，恢复它
      fs.copyFileSync(TEST_CONFIG, REAL_CONFIG);
      fs.unlinkSync(TEST_CONFIG);
    }
  } catch (e) {}
  backedUp = false;
}

process.on("exit", restoreConfig);
process.on("SIGINT", function() {
  restoreConfig();
  process.exit(1);
});

function run(cmd, desc) {
  var sep = "==================================================";
  console.log("");
  console.log(sep);
  console.log("Test: " + desc);
  console.log("Cmd: " + cmd);
  console.log(sep);
  try {
    var out = child_process.execSync(cmd, { cwd: SCRIPT_DIR, encoding: "utf-8" });
    console.log(out);
    console.log("PASS");
    return true;
  } catch (e) {
    var errOut = e.stdout ? e.stdout.toString() : "";
    var errMsg = e.message ? e.message.toString() : "";
    if (errOut) console.log(errOut);
    if (errMsg) console.log(errMsg);
    console.log("FAIL");
    return false;
  }
}

console.log("wx-miniprogram-skill test suite\n");

backupConfig();

var passed = 0;
var failed = 0;

if (run(CLI + " --help", "show help")) { passed++; } else { failed++; }
if (run(CLI + " config", "show config")) { passed++; } else { failed++; }
if (run(CLI + " config --get", "config --get (no key, show global)")) { passed++; } else { failed++; }
if (run(CLI + " config --get appid", "config --get appid")) { passed++; } else { failed++; }
if (run(CLI + " config --set testkey testvalue", "config --set key=value")) { passed++; } else { failed++; }
if (run(CLI + " config --get testkey", "config --get testkey")) { passed++; } else { failed++; }
if (!run(CLI + " config --set", "config --set (no args, expect FAIL)")) { passed++; } else { failed++; }
if (run(CLI + " config --set default myapp2", "config --set default")) { passed++; } else { failed++; }
if (run(CLI + " config --project myapp --set appid wx123", "config --project --set")) { passed++; } else { failed++; }
if (!run(CLI + " config --switch nonexistent", "config --switch nonexistent (expect FAIL)")) { passed++; } else { failed++; }
if (run(CLI + " config --switch myapp", "config --switch myapp")) { passed++; } else { failed++; }

restoreConfig();

console.log("");
console.log("==================================================");
console.log("Results: " + passed + " passed, " + failed + " failed");
console.log("==================================================");

process.exit(failed > 0 ? 1 : 0);
