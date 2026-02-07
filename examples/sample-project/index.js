/**
 * Sample buggy application for MindCore Sentinel demo.
 * Contains intentional bugs for demonstration purposes.
 */

const http = require('http');

// Bug 1: Undefined variable reference
function processData(input) {
  if (input === undefined) {
    return defaultValue; // ReferenceError: defaultValue is not defined
  }
  return input.toString();
}

// Bug 2: Type error - calling method on wrong type
function formatUser(user) {
  const name = user.name.toUpperCase();
  const age = user.age.toUpperCase(); // TypeError: age is a number, not a string
  return `${name} (${age})`;
}

// Bug 3: Array index out of bounds scenario
function getTopItems(items, count) {
  const results = [];
  for (let i = 0; i <= count; i++) { // Off-by-one: should be < not <=
    results.push(items[i].name);
  }
  return results;
}

// Bug 4: Unhandled promise rejection
async function fetchData(url) {
  const response = await fetch(url); // fetch may not exist in older Node
  const data = await response.json();
  return data;
}

// Main execution
console.log("Starting sample application...");

try {
  console.log(processData(undefined));
} catch (e) {
  console.error("Bug found:", e.message);
}

try {
  console.log(formatUser({ name: "Alice", age: 30 }));
} catch (e) {
  console.error("Bug found:", e.message);
}

try {
  const items = [{ name: "A" }, { name: "B" }, { name: "C" }];
  console.log(getTopItems(items, 3)); // Will fail: items[3] is undefined
} catch (e) {
  console.error("Bug found:", e.message);
}

console.log("Sample application finished.");
