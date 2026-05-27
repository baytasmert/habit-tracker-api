// load-test.js — k6 load test for Habit Tracker API
// Demo: 1 dk, 10→100 VU ramp-up, realistic habit CRUD workflow
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://localhost:8001';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // ramp up to 10 VU
    { duration: '20s', target: 50 },   // ramp up to 50 VU
    { duration: '20s', target: 100 },  // ramp up to 100 VU
    { duration: '10s', target: 0 },    // ramp down to 0
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'],
    'checks': ['rate>0.99'],
  },
};

export default function () {
  // Realistic user workflow: health check → create habit → list → get → update → delete

  // 1. Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health status 200': (r) => r.status === 200,
  });
  sleep(Math.random() * 2 + 1); // 1-3s think time

  // 2. Create a new habit
  const habitPayload = JSON.stringify({
    name: `Habit ${Math.random()}`,
    description: 'Test habit for performance testing',
    frequency: 'daily',
  });

  const createRes = http.post(`${BASE_URL}/habits`, habitPayload, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(createRes, {
    'create habit status 200': (r) => r.status === 200 || r.status === 201,
    'create habit response time': (r) => r.timings.duration < 500,
  });
  sleep(Math.random() * 2 + 1);

  // Extract habit ID from response
  let habitId = null;
  if (createRes.status === 200 || createRes.status === 201) {
    try {
      const body = JSON.parse(createRes.body);
      habitId = body.id || body.habit_id;
    } catch (e) {
      habitId = Math.floor(Math.random() * 1000); // fallback
    }
  }

  // 3. List all habits
  const listRes = http.get(`${BASE_URL}/habits`);
  check(listRes, {
    'list habits status 200': (r) => r.status === 200,
    'list habits response time': (r) => r.timings.duration < 500,
  });
  sleep(Math.random() * 2 + 1);

  // 4. Get specific habit (if we have ID)
  if (habitId) {
    const getRes = http.get(`${BASE_URL}/habits/${habitId}`);
    check(getRes, {
      'get habit status': (r) => r.status === 200 || r.status === 404,
      'get habit response time': (r) => r.timings.duration < 500,
    });
    sleep(Math.random() * 2 + 1);

    // 5. Update habit
    const updatePayload = JSON.stringify({
      name: `Updated Habit ${Math.random()}`,
      description: 'Updated for performance test',
      frequency: 'weekly',
    });

    const updateRes = http.put(`${BASE_URL}/habits/${habitId}`, updatePayload, {
      headers: { 'Content-Type': 'application/json' },
    });
    check(updateRes, {
      'update habit status': (r) => r.status === 200 || r.status === 404,
      'update habit response time': (r) => r.timings.duration < 500,
    });
    sleep(Math.random() * 2 + 1);

    // 6. Delete habit
    const deleteRes = http.del(`${BASE_URL}/habits/${habitId}`);
    check(deleteRes, {
      'delete habit status': (r) => r.status === 200 || r.status === 204 || r.status === 404,
      'delete habit response time': (r) => r.timings.duration < 500,
    });
    sleep(Math.random() * 2 + 1);
  }
}
