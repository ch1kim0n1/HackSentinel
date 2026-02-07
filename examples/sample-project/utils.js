/**
 * Utility functions with intentional bugs for Sentinel demo.
 */

// Bug: Division by zero scenario
function calculateAverage(numbers) {
  const sum = numbers.reduce((a, b) => a + b, 0);
  return sum / numbers.length; // NaN when numbers is empty array
}

// Bug: Infinite loop risk
function findItem(arr, target) {
  let i = 0;
  while (arr[i] !== target) {
    i++;
    // No bounds check - infinite loop if target not in array
  }
  return i;
}

module.exports = { calculateAverage, findItem };
