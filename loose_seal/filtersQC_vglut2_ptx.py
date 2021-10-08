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

##### dlpag #####

# dlpag_vglut2_190115_c3_LDEBD_OP_VC_clear_nointerval_1
# prominence (25-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = 30, QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vglut2_190117_c1_LDEBJ_OP_VC_clear_nointerval_1
# prominence (50-300), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = 100
    )

# dlpag_vglut2_190117_c7_LDEBP_OP_VC_clear_nointerval_2
# prominence (25-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = -250, QC_pb_max = -20,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vglut2_190208_c3_LDEBT_OP_VC_clear_nointerval_1
# prominence (100-300), peak (-300-0)
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

# dlpag_vglut2_200715_c11_LDECD_OP_VC_clear_nointerval_1
# prominence (45-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vglut2_200716_c9_LDECJ_OP_VC_clear_nointerval_1
# prominence (30-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vglut2_201117_c10_LDECW_OP_VC_clear_nointerval_1
# prominence (50-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vglut2_201117_c7_LDECT_OP_VC_clear_nointerval_1
# prominence (75-400), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = float('inf')
    )

# dlpag_vglut2_201119_c8_LDECZ_OP_VC_clear_nointerval_1
# prominence (75-400), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = float('inf')
    )

# dlpag_vglut2_201120_c7_LDEDE_OP_VC_clear_nointerval_2
# prominence (40-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6, QC_pw_max = 25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = float('inf')
    )


##### dmpag #####

# dmpag_vglut2_190115_c5_LDEBF_OP_VC_clear_nointerval_3
# prominence (50-150), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = 150,
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = 30,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vglut2_190117_c6_LDEBO_OP_VC_clear_nointerval_5
# prominence (40-200), peak (-150-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -80,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_190117_c8_LDEBQ_OP_VC_clear_nointerval_1
# prominence (40-150), peak (-150-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_190208_c4_LDEBU_OP_VC_clear_nointerval_1
# prominence (35-150), peak (-150-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200715_c10_LDECC_OP_VC_clear_nointerval_1
# prominence (25-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -30,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200715_c4_LDEBZ_OP_VC_clear_nointerval_1
# prominence (30-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = 30,
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200715_c5_LDECA_OP_VC_clear_nointerval_2
# prominence (30-100), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -25,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200715_c9_LDECB_OP_VC_clear_nointerval_1
# prominence (25-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -15,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200716_c4_LDECE_OP_VC_clear_nointerval_2
# prominence (100-200), peak (-150-0)
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

# dmpag_vglut2_200716_c5_LDECF_OP_VC_clear_nointerval_1
# prominence (100-400), peak (-400-0)
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

# dmpag_vglut2_200716_c6_LDECG_OP_VC_clear_nointerval_1
# prominence (25-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200716_c7_LDECH_OP_VC_clear_nointerval_1
# prominence (24-50), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_200716_c8_LDECI_OP_VC_clear_nointerval_1
# prominence (30-100), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_201116_c6_LDECL_OP_VC_clear_nointerval_1
# prominence (75-350), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = 300,
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = 7, QC_lb_max = float('inf'),
    QC_rb_min = 7, QC_rb_max = float('inf')
    )

# dmpag_vglut2_201116_c7_LDECM_OP_VC_clear_nointerval_1
# prominence (50-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vglut2_201116_c9_LDECO_OP_VC_clear_nointerval_1
# prominence (35-80), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = -80, QC_pb_max = -20,
    QC_lb_min = 4, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vglut2_201117_c6_LDECS_OP_VC_clear_nointerval_1
# prominence (75-150), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -10,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_201119_c10_LDEDB_OP_VC_clear_nointerval_1
# prominence (40-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -10,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vglut2_201119_c7_LDECY_OP_VC_clear_nointerval_1
# prominence (75-250), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -30,
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vglut2_201120_c9_LDEDG_OP_VC_clear_nointerval_1
# prominence (35-200), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 7, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )


##### lpag #####

##### vlpag #####