const fs = require('fs');
const path = require('path');
const Module = require('module');

const partCount = 12;
const source = Buffer.concat(
  Array.from({ length: partCount }, (_, index) =>
    fs.readFileSync(path.join(__dirname, `xhs_creator_sign_other_part${index + 1}.js`))
  )
).toString('utf8');

const filename = path.join(__dirname, 'xhs_creator_sign_other.compiled.js');
const child = new Module(filename, module.parent || module);
child.filename = filename;
child.paths = Module._nodeModulePaths(__dirname);
child._compile(source, filename);

module.exports = child.exports;
