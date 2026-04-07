const { execSync } = require('child_process');
const os = require('os');

function safeMessage(error) {
  return error?.stderr?.toString()?.trim()
    || error?.stdout?.toString()?.trim()
    || error?.message
    || 'Unknown error';
}

function isNetworkError(error) {
  const msg = `${safeMessage(error)} ${error?.code || ''}`.toLowerCase();
  return [
    'enotfound',
    'econnreset',
    'eai_again',
    'etimedout',
    'network',
    'unable to resolve host',
    'getaddrinfo',
  ].some((k) => msg.includes(k));
}

function run(command) {
  return execSync(command, {
    stdio: ['ignore', 'pipe', 'pipe'],
    encoding: 'utf8',
    shell: '/bin/bash',
  });
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function installBrew(formula) {
  try {
    run(`brew install ${shellQuote(formula)}`);
    return { name: formula, status: 'installed', message: `Installed brew formula: ${formula}` };
  } catch (error) {
    return {
      name: formula,
      status: 'failed',
      message: isNetworkError(error)
        ? `Network error while installing brew formula ${formula}: ${safeMessage(error)}`
        : `Failed to install brew formula ${formula}: ${safeMessage(error)}`,
    };
  }
}

function installNpm(pkg) {
  const home = os.homedir();
  let prefix = '';

  try {
    prefix = run('npm config get prefix').trim();
    run(`npm install -g ${shellQuote(pkg)}`);
    return { name: pkg, status: 'installed', message: `Installed npm package: ${pkg}` };
  } catch (error) {
    const msg = safeMessage(error);
    const isEacces = `${msg} ${error?.code || ''}`.toLowerCase().includes('eacces');
    const isUserPrefix = prefix.startsWith(home);

    if (isEacces && !isUserPrefix) {
      try {
        run(`npm install -g --location=user ${shellQuote(pkg)}`);
        return { name: pkg, status: 'installed', message: `Installed npm package with user fallback: ${pkg}` };
      } catch (fallbackError) {
        return {
          name: pkg,
          status: 'failed',
          message: isNetworkError(fallbackError)
            ? `Network error while installing npm package ${pkg}: ${safeMessage(fallbackError)}`
            : `Failed to install npm package ${pkg}: ${safeMessage(fallbackError)}`,
        };
      }
    }

    return {
      name: pkg,
      status: 'failed',
      message: isNetworkError(error)
        ? `Network error while installing npm package ${pkg}: ${msg}`
        : `Failed to install npm package ${pkg}: ${msg}`,
    };
  }
}

function installPip(pkg) {
  try {
    run(`pip install ${shellQuote(pkg)}`);
    return { name: pkg, status: 'installed', message: `Installed pip package: ${pkg}` };
  } catch (error) {
    const msg = safeMessage(error);
    const isEacces = `${msg} ${error?.code || ''}`.toLowerCase().includes('eacces');

    if (isEacces) {
      try {
        run(`pip install --user ${shellQuote(pkg)}`);
        return { name: pkg, status: 'installed', message: `Installed pip package with --user fallback: ${pkg}` };
      } catch (fallbackError) {
        return {
          name: pkg,
          status: 'failed',
          message: isNetworkError(fallbackError)
            ? `Network error while installing pip package ${pkg}: ${safeMessage(fallbackError)}`
            : `Failed to install pip package ${pkg}: ${safeMessage(fallbackError)}`,
        };
      }
    }

    return {
      name: pkg,
      status: 'failed',
      message: isNetworkError(error)
        ? `Network error while installing pip package ${pkg}: ${msg}`
        : `Failed to install pip package ${pkg}: ${msg}`,
    };
  }
}

module.exports = {
  installBrew,
  installNpm,
  installPip,
};
