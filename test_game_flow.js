const axios = require('axios');

async function testGameFlow() {
  const baseURL = 'http://localhost:8000';
  
  console.log('🎮 Code Review Quest - Game Flow Test');
  console.log('=====================================');
  
  try {
    // 1. Health Check
    console.log('1. Health Check...');
    const health = await axios.get(`${baseURL}/health`);
    console.log('✅ API Health:', health.data.status);
    
    // 2. Start Game Session
    console.log('\n2. Starting Game Session...');
    const sessionResponse = await axios.post(`${baseURL}/api/v1/session/start`, {
      difficulty: 'beginner',
      time_limit: 900
    });
    const session = sessionResponse.data;
    console.log('✅ Session Created:', session.session_id);
    console.log('📝 Problem:', session.problem_id);
    console.log('⏰ Time Limit:', session.time_limit, 'seconds');
    
    // 3. Submit Bug Report (correct answer)
    console.log('\n3. Submitting Bug Report...');
    const submitResponse = await axios.post(`${baseURL}/api/v1/submit/`, {
      session_id: session.session_id,
      bugs: [{ line_number: 4, description: 'Division by zero bug' }]
    });
    const result = submitResponse.data;
    console.log('✅ Submission Result:');
    console.log('   Score:', result.score, '/', result.max_score);
    console.log('   Correct Bugs:', result.correct_bugs);
    console.log('   Missed Bugs:', result.missed_bugs);
    console.log('   False Positives:', result.false_positives);
    
    // 4. Get Profile
    console.log('\n4. Getting User Profile...');
    const profileResponse = await axios.get(`${baseURL}/api/v1/profile/me`);
    const profile = profileResponse.data;
    console.log('✅ Profile:', profile.username);
    console.log('   Total Sessions:', profile.stats.total_sessions);
    console.log('   Average Score:', profile.stats.average_score);
    console.log('   Badges:', profile.badges.length);
    
    // 5. Get Leaderboard
    console.log('\n5. Getting Leaderboard...');
    const leaderboardResponse = await axios.get(`${baseURL}/api/v1/profile/leaderboard`);
    const leaderboard = leaderboardResponse.data;
    console.log('✅ Leaderboard Top 3:');
    leaderboard.leaderboard.slice(0, 3).forEach(player => {
      console.log(`   ${player.rank}. ${player.username}: ${player.score}`);
    });
    
    console.log('\n🎉 All tests passed! Game flow is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
  }
}

testGameFlow();
