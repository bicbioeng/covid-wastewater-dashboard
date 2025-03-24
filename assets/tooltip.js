window.dccFunctions = window.dccFunctions || {};
window.dccFunctions.formatNumber = function (value) {
  // Implement your number formatting logic here
  if (value === undefined || value === null) {
    return "";
  }

  value = Number(value);
  print(value);

  const num_million = value / 1000000;

  if (num_million >= 1000) {
    return (num_million / 1000).toFixed(2) + "B";
  } else if (num_million >= 1) {
    return num_million.toFixed(2) + "M";
  } else {
    return value.toFixed(2);
  }
};
