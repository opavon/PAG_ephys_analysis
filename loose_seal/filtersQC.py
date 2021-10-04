# Defaults
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = 20, QC_wh_max = float('inf'),
    QC_pw_min = 2, QC_pw_max = 5,
    QC_ph_min = 50, QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -85,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_171114_c4_LIAM_OP_clear_VC_1
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = 0, QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_171117_c1_LIAR_OP_clear_VC_2
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -80,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = 12
    )