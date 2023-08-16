const convertRemToPixels = (rem) => {
  return rem * parseFloat(getComputedStyle(document.documentElement).fontSize);
};

const getWidthRelativeToInput = (widthInPx, input) => {
  return (widthInPx /  input.getBoundingClientRect().width) * 100;
};

const getThumbPosition = (value, input) => {
  const thumbWidth = convertRemToPixels(1);
  const thumbHalfWidth = thumbWidth / 2;
  const totalInputWidth = input.getBoundingClientRect().width;

  const positionInPixels = (((value - input.min) / (input.max - input.min)) * ((totalInputWidth - thumbHalfWidth) - thumbHalfWidth)) + thumbHalfWidth;

  return getWidthRelativeToInput(positionInPixels, input);
};

const debounce = (job, ms) => {
  let timerId = null;

  return () => {
    if (timerId) {
      clearTimeout(timerId);
    }

    timerId = setTimeout(job, ms);
  };
};

const removeChildren = (block) => {
  while (block.hasChildNodes()) {
    block.firstChild.remove();
  }
};

const votingRangeInputs = Array.from(document.querySelectorAll('.voting-range-input'));
const votingRangeLine = document.querySelector('.voting-range-line');
const votingRangeOptions = document.querySelectorAll('.voting-range-option');

const setDateLabel = (value, label) => {
  label.textContent = votingRangeOptions[value].textContent;
  label.dataset.value = votingRangeOptions[value].dataset.value;
};

const votingRangeFirstDate = document.querySelector('.voting-range-first-date');
setDateLabel(0, votingRangeFirstDate);
const votingRangeSecondDate = document.querySelector('.voting-range-second-date');
setDateLabel(votingRangeOptions.length - 1, votingRangeSecondDate);
const votingRangeState = {
  from: +votingRangeInputs.find((input) => input.dataset.kind === 'from')?.value,
  to: +votingRangeInputs.find((input) => input.dataset.kind === 'to')?.value,
};
let lastResults = {};

const isResultsEqual = (current, last) => {
  if (current.length !== Object.keys(last).length) {
    return false;
  }

  const isTeamsChanged = current.some((team) => !last[team.id]);

  if (isTeamsChanged) {
    return false;
  }

  const isCriteriaChanged = current.some((team) => {
    if (team.criteria.length !== Object.keys(last[team.id].criteria).length) {
      return true;
    }

    return team.criteria.some((criterion) => !last[team.id].criteria[criterion.id]);
  });

  if (isCriteriaChanged) {
    return false;
  }

  const isMembersChanged = current.some((team) => {
    if (team.members.length !== Object.keys(last[team.id].members).length) {
      return true;
    }

    return team.members.some((member) => !last[team.id].members[member.id]);
  });

  return !isMembersChanged;
};

const weeklyResultsContainer = document.querySelector('#weekly-results-container');

const updateResults = async () => {
  const response = await fetch('/get_results_of_weekly_voting?' + new URLSearchParams({
      start_date: votingRangeOptions[votingRangeState.from].dataset.value,
      end_date: votingRangeOptions[votingRangeState.to].dataset.value,
    }));

  const { results } = await response.json();

  const MAX_LINE_WIDTH_IN_REM = 22;

  if (weeklyResultsContainer.hasChildNodes() && isResultsEqual(results, lastResults)) {
    results.forEach((result) => {
      result.criteria.forEach((criterion) => {
        const line = document.querySelector(`.weekly-result-stat-rectangle[data-criterion-id="${criterion.id}"][data-team-id="${result.id}"]`);
        const summary = document.querySelector(`.weekly-result-stat-summary[data-criterion-id="${criterion.id}"][data-team-id="${result.id}"]`);

        line.style.width = `${(criterion.gained / criterion.total) * MAX_LINE_WIDTH_IN_REM}rem`;
        summary.textContent = `${criterion.gained} / ${criterion.total}`;
      });
    });
  } else {
    removeChildren(weeklyResultsContainer);

    results.forEach((result) => {
      const card = document.createElement('article');
      card.classList.add('weekly-results-card');

      const title = document.createElement('h3');
      title.classList.add('weekly-result-name');
      title.textContent = result.name;
      card.appendChild(title);

      const body = document.createElement('div');
      body.classList.add('weekly-result-body');
      card.appendChild(body);

      const membersContainer = document.createElement('div');
      membersContainer.classList.add('weekly-result-members-container');
      body.appendChild(membersContainer);

      const members = document.createElement('div');
      members.classList.add('weekly-result-members');
      const membersList = document.createElement('ul');
      result.members.forEach((member) => {
        const memberRow = document.createElement('li');
        memberRow.classList.add('weekly-result-member');
        memberRow.textContent = `${member.name} ${member.surname}`;
        membersList.appendChild(memberRow);
      });
      members.appendChild(membersList);
      const membersLabel = document.createElement('span');
      membersLabel.classList.add('weekly-result-members-label');
      membersLabel.textContent = 'СОСТАВ КОМАНДЫ';
      members.appendChild(membersLabel);
      membersContainer.appendChild(members);

      const diagramsContainer = document.createElement('div');
      diagramsContainer.classList.add('weekly-result-diagram-container');
      body.appendChild(diagramsContainer);

      result.criteria.forEach((criterion) => {
        const statContainer = document.createElement('div');
        statContainer.classList.add('weekly-result-stat-container');
        diagramsContainer.appendChild(statContainer);

        const statLabel = document.createElement('span');
        statLabel.classList.add('weekly-result-stat-label');
        statLabel.textContent = criterion.name
        statContainer.appendChild(statLabel);

        const stat = document.createElement('div');
        stat.classList.add('weekly-result-stat');
        statContainer.appendChild(stat);

        const line = document.createElement('hr');
        line.classList.add('weekly-result-stat-rectangle');
        line.dataset.criterionId = criterion.id;
        line.dataset.teamId = result.id;
        line.style.width = `${(criterion.gained / criterion.total) * MAX_LINE_WIDTH_IN_REM}rem`;
        stat.appendChild(line);

        const summary = document.createElement('span');
        summary.classList.add('weekly-result-stat-summary');
        summary.dataset.criterionId = criterion.id;
        summary.dataset.teamId = result.id;
        summary.textContent = `${criterion.gained} / ${criterion.total}`;
        stat.appendChild(summary);
      });

      weeklyResultsContainer.appendChild(card);
    });
  }

  lastResults = results.reduce((store, current) => {
    return {
      ...store,
      [current.id]: {
        ...current,
        criteria: current.criteria.reduce((store, current) => {
          return { ...store, [current.id]: current };
        }, {}),
        members: current.members.reduce((store, current) => {
          return { ...store, [current.id]: current };
        }, {}),
      },
    };
  }, {});
};

updateResults().catch(console.error);

const updateResultsDebounced = debounce(updateResults, 250);

votingRangeInputs.forEach((input) => {
  input.addEventListener('input', (event) => {
    votingRangeState[event.target.dataset.kind] = +event.target.value;

    if (votingRangeState.from > votingRangeState.to) {
      [votingRangeState.from, votingRangeState.to] = [votingRangeState.to, votingRangeState.from];

      const votingFromInput = votingRangeInputs.find((input) => input.dataset.kind === 'from');
      const votingToInput = votingRangeInputs.find((input) => input.dataset.kind === 'to');

      [votingFromInput.dataset.kind, votingToInput.dataset.kind] = [votingToInput.dataset.kind, votingFromInput.dataset.kind];
    }

    const fromThumbPosition = getThumbPosition(votingRangeState.from, input);
    const toThumbPosition = getThumbPosition(votingRangeState.to, input);

    votingRangeLine.style.background = `linear-gradient(to right, transparent ${fromThumbPosition}%, black ${fromThumbPosition}%, black ${toThumbPosition}%, transparent ${toThumbPosition}%)`;
    votingRangeFirstDate.style.left = `${fromThumbPosition - getWidthRelativeToInput(votingRangeFirstDate.getBoundingClientRect().width, input)}%`;
    setDateLabel(votingRangeState.from, votingRangeFirstDate);
    votingRangeSecondDate.style.left = `${toThumbPosition}%`;
    setDateLabel(votingRangeState.to, votingRangeSecondDate);
    votingRangeSecondDate.style.display = votingRangeState.from === votingRangeState.to ? 'none' : 'block';

    updateResultsDebounced();
  });
});