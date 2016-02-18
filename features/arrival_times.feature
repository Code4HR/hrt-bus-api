# language: en

# https://github.com/Code4HR/hrt-bus-api/issues/79
Feature: Arrival times
  As a citizen
  I want to get arrival times for public transportation
  so I can rely on HRT

  Scenario: Stop arrival times
    Given the adherence data from the API
    When I look up a certain stop
    Then I will get approximate arrival times

