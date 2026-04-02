// 技能执行代码
async function executeSkill(input, context) {
  try {
    // 使用环境变量中的 API 地址，优先使用 HTTPS
    const apiUrl = process.env.NOVAI360_API_URL || 'https://api.novai360.com/api/litechat/chat';
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: input,
        userId: context.userId || context.user_id,
        source: 'ClawHub'
      })
    });

    const data = await response.json();
    if (data.success) {
      return {
        success: true,
        result: data.data.answer,
        remainingCalls: data.remainingCalls,
        userId: data.userId
      };
    } else {
      return {
        success: false,
        error: data.message
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message || 'API 调用失败'
    };
  }
}

// 获取技能列表
async function getSkills() {
  try {
    const apiUrl = 'http://your-api-url/api/litechat/skills';
    const response = await fetch(apiUrl);
    const data = await response.json();
    return data;
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 获取技能分类
async function getSkillCategories() {
  try {
    const apiUrl = 'http://your-api-url/api/litechat/skill-categories';
    const response = await fetch(apiUrl);
    const data = await response.json();
    return data;
  } catch (error) {
    return { success: false, error: error.message };
  }
}

module.exports = {
  execute: executeSkill,
  getSkills: getSkills,
  getSkillCategories: getSkillCategories
};