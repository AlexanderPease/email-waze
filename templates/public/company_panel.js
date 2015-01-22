// Loads and displays Company panel for a given company dict
function showCompanyPanelLoading(c) {
  panelHtml = '<div><img src="' + c['logo'] + '" height="32" weight="32" \
    style="margin-bottom:4px"><a href="http://';
  panelHtml += c['domain'] + '" target="_blank">';
  panelHtml += c['name'] + '</a><div>Loading...</div></div>';
  $('#company-panel .panel-body').empty().append(panelHtml);
  $('#company-panel').show();
}

// Loads and displays Company panel for a given company dict
// c is company_stats dict of info to display
function showCompanyPanel(c) {
  panelHtml = '<div>';
  if (c['logo']) {
    panelHtml += '<img src="' + c['logo'] + '" height="32" weight="32" \
    style="margin-bottom:4px">';
  }
  panelHtml += '<a href="http://';
  panelHtml += c['domain'] + '" target="_blank">';
  panelHtml += c['name'] + '</a><div>'
  panelHtml += 'Strongest Connection: ' + c['strongest_connection'] + '</div></div>';
  $('#company-panel .panel-body').empty().append(panelHtml);
  $('#company-panel').show();
}
