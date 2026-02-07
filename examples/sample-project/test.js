/**
 * Sample test file with intentional failures for Sentinel demo.
 */

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  PASS: ${message}`);
  } else {
    failed++;
    console.error(`  FAIL: ${message}`);
  }
}

console.log("Running tests...\n");

// Test 1: Should pass
assert(1 + 1 === 2, "basic addition");

// Test 2: Should fail (intentional bug)
assert("5" === 5, "string equals number (strict)");

// Test 3: Should pass
assert([1, 2, 3].length === 3, "array length");

// Test 4: Should fail (intentional bug)
const obj = { a: 1 };
assert(obj.b !== undefined, "missing property check");

console.log(`\nResults: ${passed} passed, ${failed} failed`);

if (failed > 0) {
  process.exit(1);
}
