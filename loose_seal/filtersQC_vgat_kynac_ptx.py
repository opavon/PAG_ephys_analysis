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

# dlpag_vgat_190122_c1_LDIAA_OP_VC_clear_nointerval_2
# prominence (38-150), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4.8, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -25,
    QC_lb_min = 7, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dlpag_vgat_200717_c4_LDIAL _OP_VC_clear_nointerval_1
# prominence (200-600), peak (-500-0)
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

# dlpag_vgat_200717_c5_LDIAM_OP_VC_clear_nointerval_1
# prominence (150-400), peak (-350-0)
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

# dlpag_vgat_200720_c9_LDIAS_OP_VC_clear_nointerval_1
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

# dlpag_vgat_201105_c2_LDIBC_OP_VC_clear_nointerval_1
# prominence (90-200), peak (-200-50)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 6,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dlpag_vgat_201105_c5_LDIBF_OP_VC_clear_nointerval_1
# prominence (100-200), peak (-200-0)
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

# dlpag_vgat_201125_c5_LDIBM_OP_VC_clear_nointerval_2
# prominence (80-500), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max =  float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201126_c4_LDIBS_OP_VC_clear_nointerval_2
# prominence (125-200), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max =  float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201126_c4_LDIBS_OP_VC_clear_nointerval_3
# prominence (105-270), peak (-300-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 50,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = 100
    )

# dlpag_vgat_201201_c2_LDIBU_OP_VC_clear_nointerval_2
# prominence (50-200), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201201_c5_LDIBX_OP_VC_clear_nointerval_1
# prominence (70-200), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201202_c4_LDIBZ_OP_VC_clear_nointerval_1
# prominence (35-120), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = -66, QC_pb_max = -25,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201202_c5_LDICA_OP_VC_clear_nointerval_1
# prominence (90-165), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3.5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 4.1, QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201202_c7_LDICC_OP_VC_clear_nointerval_1
# prominence (125-280), peak (-300-100)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201203_c5_LDICG_OP_VC_clear_nointerval_3
# prominence (100-200), peak (-200-0)
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

# dlpag_vgat_201215_c3_LDICL_OP_VC_clear_nointerval_1
# prominence (65-160), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6, QC_pw_max = 9,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dlpag_vgat_201215_c9_LDICR_OP_VC_clear_nointerval_1
# prominence (70-200), peak (-200-0)
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
    QC_rb_min = float('-inf'), QC_rb_max = 120
    )


##### dmpag #####

# dmpag_vgat_190123_c2_LDIAF_OP_VC_clear_nointerval_1
# prominence (105-200), peak (-200-0)
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

# dmpag_vgat_200720_c7_LDIAQ_OP_VC_clear_nointerval_1
# prominence (40-300), peak (NA)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 7,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_200720_c8_LDIAR_OP_VC_clear_nointerval_1
# prominence (60-150), peak (-200-0)
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

# dmpag_vgat_201102_c3_LDIAX_OP_VC_clear_nointerval_2
# prominence (140-500), peak (-350-0)
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
    QC_rb_min = 5, QC_rb_max = 20
    )

# dmpag_vgat_201102_c4_LDIAY_OP_VC_clear_nointerval_1
# prominence (50-125), peak (-85-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 4, QC_lb_max = float('inf'),
    QC_rb_min = 4, QC_rb_max = 80
    )

# dmpag_vgat_201102_c7_LDIBA_OP_VC_clear_nointerval_2
# prominence (50-200), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -20,
    QC_lb_min = 4, QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = 20
    )

# dmpag_vgat_201105_c3_LDIBD_OP_VC_clear_nointerval_2
# prominence (40-150), peak (-100-0)
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

# dmpag_vgat_201105_c4_LDIBE_OP_VC_clear_nointerval_2
# prominence (60-150), peak (-150-0)
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

# dmpag_vgat_201105_c5_LDIBF_OP_VC_clear_nointerval_2
# prominence (110-250), peak (-250-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3.95, QC_pw_max = 6.25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = 100
    )

# dmpag_vgat_201105_c6_LDIBG_OP_VC_clear_nointerval_1
# prominence (55-110), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4.5, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = 63.5
    )

# dmpag_vgat_201105_c7_LDIBH_OP_VC_clear_nointerval_2
# prominence (85-140), peak (-150-0)
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

# dmpag_vgat_201105_c8_LDIBI_OP_VC_clear_nointerval_2
# prominence (53-150), peak (-150-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -10,
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vgat_201125_c3_LDIBK_OP_VC_clear_nointerval_2
# prominence (45-85), peak (-75-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 2.9, QC_pw_max = 9,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201125_c6_LDIBN_OP_VC_clear_nointerval_1
# prominence (100-400), peak (-350-0)
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

# dmpag_vgat_201125_c8_LDIBP_OP_VC_clear_nointerval_1
# prominence (125-250), peak (-200-0)
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

# dmpag_vgat_201125_c9_LDIBQ_OP_VC_clear_nointerval_1
# prominence (42-100), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 12,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -25,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201201_c3_LDIBV_OP_VC_clear_nointerval_1
# prominence (50-200), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201201_c4_LDIBW_OP_VC_clear_nointerval_3
# prominence (45-150), peak (-150-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201202_c4_LDIBZ_OP_VC_clear_nointerval_2
# prominence (70-170), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3.5, QC_pw_max = 7.5,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -40,
    QC_lb_min = 5, QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# dmpag_vgat_201203_c2_LDICD_OP_VC_clear_nointerval_1
# prominence (35-55), peak (-50-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6.5, QC_pw_max = 25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 8, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = float('inf')
    )

# dmpag_vgat_201203_c4_LDICF_OP_VC_clear_nointerval_1
# prominence (80-253), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3.75, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = 25
    )

# dmpag_vgat_201203_c7_LDICI_OP_VC_clear_nointerval_1
# prominence (100-250), peak (-250-0)
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

# dmpag_vgat_201203_c8_LDICJ_OP_VC_clear_nointerval_2
# prominence (79-270), peak (-250-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5.5, QC_pw_max = 13,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = 7.5, QC_rb_max = float('inf')
    )

# dmpag_vgat_201215_c2_LDICK_OP_VC_clear_nointerval_1
# prominence (170-500), peak (-400-100)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4.1, QC_pw_max = 8,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201215_c5_LDICN_OP_VC_clear_nointerval_3
# prominence (80-190), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 6.05, QC_pw_max = 25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201215_c8_LDICQ_OP_VC_clear_nointerval_1
# prominence (80-180), peak (-300-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201216_c4_LDICS_OP_VC_clear_nointerval_2
# prominence (40-100), peak (-100-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = 15,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# dmpag_vgat_201216_c5_LDICT_OP_VC_clear_nointerval_1
# prominence (80-125), peak (-200-0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 25,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = 0,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )


##### lpag #####

# lpag_vgat_201125_c4_LDIBL_OP_VC_clear_nointerval_1
# prominence (55, 120), peak (-150, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3.6, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# lpag_vgat_201125_c7_LDIBO_OP_VC_clear_nointerval_1
# prominence (100, 180), peak (-200, 0)
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

# lpag_vgat_201201_c6_LDIBY_OP_VC_clear_nointerval_3
# prominence (43, 90), peak (-100, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4.5, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = 5, QC_rb_max = float('inf')
    )

# lpag_vgat_201203_c6_LDICH_OP_VC_clear_nointerval_1
# prominence (50, 150), peak (-85, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = 15,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# lpag_vgat_201215_c4_LDICM_OP_VC_clear_nointerval_1
# prominence (135, 300), peak (-300, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 4, QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -100,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )


##### vlpag #####

# vlpag_vgat_190123_c1_LDIAE_OP_VC_clear_nointerval_2
# prominence (80, 160), peak (-150, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 3, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# vlpag_vgat_201202_c6_LDICB_OP_VC_clear_nointerval_1
# prominence (100, 250), peak (-200, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 7, QC_pw_max = 20,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -90,
    QC_lb_min = 9, QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )

# vlpag_vgat_201203_c3_LDICE_OP_VC_clear_nointerval_1
# prominence (55, 125), peak (-100, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = 5, QC_pw_max = 10,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = 6, QC_lb_max = float('inf'),
    QC_rb_min = 6, QC_rb_max = float('inf')
    )

# vlpag_vgat_201215_c6_LDICO_OP_VC_clear_nointerval_2
# prominence (60, 120), peak (-150, 0)
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

# vlpag_vgat_201215_c7_LDICP_OP_VC_clear_nointerval_1
# prominence (140, 400), peak (-350, 0)
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = 6,
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )