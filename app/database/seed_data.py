"""
Seed data for ISO/IEC 25023:2016 Quality Catalog, Table III Mapping Rules,
and Indonesian Sample Project for demonstration and validation.
Strictly verified against ISO/IEC 25023:2016 standard tables and measure IDs.
"""

# 8 Top-Level Quality Characteristics from ISO/IEC 25023:2016 (Clause 8.2 - 8.9)
ISO_QUALITY_CHARACTERISTICS = [
    {
        "iso_number": 1,
        "code": "QC-1",
        "name": "Functional suitability",
        "description": "Tingkat sejauh mana suatu produk atau sistem menyediakan fungsi-fungsi yang memenuhi kebutuhan yang dinyatakan dan tersirat saat digunakan dalam kondisi yang ditentukan (ISO/IEC 25023:2016 Clause 8.2).",
        "subcharacteristics": [
            {
                "code": "QSC-1.1",
                "name": "Functional completeness",
                "description": "Tingkat sejauh mana rangkaian fungsi mencakup semua tugas yang ditentukan dan tujuan pengguna (Clause 8.2.1).",
                "measures": [
                    {
                        "measure_id": "FCp-1-G",
                        "name": "Functional coverage",
                        "description": "What proportion of the specified functions has been implemented?",
                        "formula": "X = 1 - A/B (A = Number of functions missing, B = Number of functions specified)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Inspeksi spesifikasi kebutuhan & pengujian fungsional",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-1.2",
                "name": "Functional correctness",
                "description": "Tingkat sejauh mana suatu produk atau sistem memberikan hasil yang benar dengan presisi yang dibutuhkan (Clause 8.2.2).",
                "measures": [
                    {
                        "measure_id": "FCr-1-G",
                        "name": "Functional correctness",
                        "description": "What proportion of functions provides the correct results?",
                        "formula": "X = 1 - A/B (A = Number of functions that are incorrect, B = Number of functions considered)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Pengujian fungsional otomatis & verifikasi hasil komputasi",
                        "dummy_target": ">= 0.99",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-1.3",
                "name": "Functional appropriateness",
                "description": "Tingkat sejauh mana fungsi-fungsi memfasilitasi penyelesaian tugas dan tujuan tertentu yang ditentukan (Clause 8.2.3).",
                "measures": [
                    {
                        "measure_id": "FAp-1-G",
                        "name": "Functional appropriateness of usage objective",
                        "description": "What proportion of the functions required by the user provides appropriate outcome to achieve a specific usage objective?",
                        "formula": "X = 1 - A/B (A = Number of functions missing or incorrect, B = Number of functions required)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "User Acceptance Testing (UAT)",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "FAp-2-G",
                        "name": "Functional appropriateness of system",
                        "description": "What proportion of the functions required by the users to achieve their objectives provides appropriate outcome?",
                        "formula": "X = Sum(Ai) / n (Ai = Appropriateness score for usage objective i, n = Number of usage objectives)",
                        "unit": "Skor rata-rata [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Evaluasi agregat kesesuaian sistem lintas skenario pengguna",
                        "dummy_target": ">= 0.95",
                        "target_unit": "skor"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 2,
        "code": "QC-2",
        "name": "Performance efficiency",
        "description": "Kinerja relatif terhadap jumlah sumber daya yang digunakan pada kondisi yang ditentukan (ISO/IEC 25023:2016 Clause 8.3).",
        "subcharacteristics": [
            {
                "code": "QSC-2.1",
                "name": "Time behaviour",
                "description": "Tingkat sejauh mana waktu respon, waktu pemrosesan, dan tingkat throughput suatu produk memenuhi kebutuhan (Clause 8.3.1).",
                "measures": [
                    {
                        "measure_id": "PTb-1-G",
                        "name": "Mean response time",
                        "description": "How long is the mean time taken by the system to respond to a user task or system task?",
                        "formula": "X = Sum(Ai) / n (Ai = Time taken to respond at i-th measurement, n = Number of responses)",
                        "unit": "Milidetik (ms)",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Performance profiling & APM telemetry log",
                        "dummy_target": "<= 300",
                        "target_unit": "ms"
                    },
                    {
                        "measure_id": "PTb-2-G",
                        "name": "Response time adequacy",
                        "description": "How well does the system response time meet the specified target?",
                        "formula": "X = A / B (A = Mean response time measured, B = Target response time specified)",
                        "unit": "Rasio kecukupan",
                        "direction": "Makin rendah makin baik (X <= 1.0)",
                        "verification_method": "Benchmark SLA load testing",
                        "dummy_target": "<= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "PTb-3-G",
                        "name": "Mean turnaround time",
                        "description": "What is the mean time taken for completion of a job or an asynchronous process?",
                        "formula": "X = Sum(Bi - Ai) / n (Ai = Start time, Bi = Complete time, n = Number of measurements)",
                        "unit": "Detik (s)",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Batch job execution monitoring",
                        "dummy_target": "<= 5",
                        "target_unit": "detik"
                    },
                    {
                        "measure_id": "PTb-5-G",
                        "name": "Mean throughput",
                        "description": "What is the mean number of jobs completed per unit time?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = Number of jobs completed, Bi = observation period)",
                        "unit": "Transaksi per detik (TPS)",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "High-concurrency stress testing",
                        "dummy_target": ">= 100",
                        "target_unit": "TPS"
                    }
                ]
            },
            {
                "code": "QSC-2.2",
                "name": "Resource utilization",
                "description": "Tingkat sejauh mana jumlah dan jenis sumber daya yang digunakan oleh produk memenuhi kebutuhan (Clause 8.3.2).",
                "measures": [
                    {
                        "measure_id": "PRu-1-G",
                        "name": "Mean processor utilization",
                        "description": "How much processor time is used to execute a given set of tasks compared to the operation time?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = CPU time used, Bi = Operation time)",
                        "unit": "Persentase (%)",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "CPU hardware counters & OS monitoring",
                        "dummy_target": "<= 70",
                        "target_unit": "%"
                    },
                    {
                        "measure_id": "PRu-2-G",
                        "name": "Mean memory utilization",
                        "description": "How much of memory is used to execute a given set of tasks compared to the available memory?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = Size of memory used, Bi = Size of memory available)",
                        "unit": "Persentase (%)",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "RAM usage telemetry profiling",
                        "dummy_target": "<= 75",
                        "target_unit": "%"
                    },
                    {
                        "measure_id": "PRu-3-G",
                        "name": "Mean I/O devices utilization",
                        "description": "How much of I/O device busy time is used to perform a given set of tasks compared to the I/O operation time?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = Duration of I/O busy time, Bi = Duration of I/O operation)",
                        "unit": "Persentase (%)",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Disk/Network I/O monitoring",
                        "dummy_target": "<= 60",
                        "target_unit": "%"
                    },
                    {
                        "measure_id": "PRu-4-S",
                        "name": "Bandwidth utilization",
                        "description": "What proportion of the available bandwidth is utilized to perform a given set of tasks?",
                        "formula": "X = A / B (A = Bandwidth measured, B = Bandwidth capacity available)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin rendah makin baik (dibawah batas saturasi)",
                        "verification_method": "Network traffic bandwidth analyzer",
                        "dummy_target": "<= 0.70",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-2.3",
                "name": "Capacity",
                "description": "Tingkat sejauh mana batas maksimum parameter produk atau sistem memenuhi kebutuhan (Clause 8.3.3).",
                "measures": [
                    {
                        "measure_id": "PCa-1-G",
                        "name": "Transaction processing capacity",
                        "description": "How many transactions can be processed per unit time?",
                        "formula": "X = A / B (A = Number of transactions completed, B = Duration of observation)",
                        "unit": "Transaksi/detik",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Load & volume testing",
                        "dummy_target": ">= 200",
                        "target_unit": "transaksi/detik"
                    },
                    {
                        "measure_id": "PCa-2-G",
                        "name": "User access capacity",
                        "description": "How many users can access the system simultaneously at a certain time?",
                        "formula": "X = Sum(Ai) / n (Ai = Maximum simultaneous users at i-th observation)",
                        "unit": "Pengguna bersamaan",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Simultaneous user concurrency test",
                        "dummy_target": ">= 500",
                        "target_unit": "pengguna"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 3,
        "code": "QC-3",
        "name": "Compatibility",
        "description": "Tingkat sejauh mana suatu produk dapat bertukar informasi dengan produk lain dan/atau menjalankan fungsinya saat berbagi lingkungan umum (ISO/IEC 25023:2016 Clause 8.4).",
        "subcharacteristics": [
            {
                "code": "QSC-3.1",
                "name": "Co-existence",
                "description": "Tingkat sejauh mana produk dapat menjalankan fungsi yang dibutuhkannya saat berbagi lingkungan umum dengan produk lain tanpa dampak merugikan (Clause 8.4.1).",
                "measures": [
                    {
                        "measure_id": "CCo-1-G",
                        "name": "Co-existence with other products",
                        "description": "What proportion of specified software products can share the environment without adverse impact on quality or functionality?",
                        "formula": "X = A / B (A = Number of co-existing software products, B = Total specified products)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Multi-application environment testing",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-3.2",
                "name": "Interoperability",
                "description": "Tingkat sejauh mana dua atau lebih sistem atau komponen dapat bertukar informasi dan menggunakan informasi yang dipertukarkan (Clause 8.4.2).",
                "measures": [
                    {
                        "measure_id": "CIn-1-G",
                        "name": "Data formats exchangeability",
                        "description": "What proportion of the specified data formats is exchangeable with other software or systems?",
                        "formula": "X = A / B (A = Number of data formats exchangeable, B = Total data formats specified)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Schema validation (FHIR/JSON/XML) & contract tests",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "CIn-2-G",
                        "name": "Data exchange protocol sufficiency",
                        "description": "What proportion of the specified data exchange protocols is supported?",
                        "formula": "X = A / B (A = Supported protocols, B = Specified protocols required)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Network protocol compliance test (REST/TLS/gRPC)",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "CIn-3-S",
                        "name": "External interface adequacy",
                        "description": "What proportion of the specified external interfaces is functional?",
                        "formula": "X = A / B (A = Number of functional external interfaces, B = Total external interfaces specified)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "End-to-end integration test suite",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 4,
        "code": "QC-4",
        "name": "Usability",
        "description": "Tingkat sejauh mana produk dapat digunakan oleh pengguna tertentu untuk mencapai tujuan dengan efektivitas, efisiensi, dan kepuasan (ISO/IEC 25023:2016 Clause 8.5).",
        "subcharacteristics": [
            {
                "code": "QSC-4.1",
                "name": "Appropriateness recognizability",
                "description": "Tingkat sejauh mana pengguna dapat mengenali apakah produk atau sistem sesuai dengan kebutuhan mereka dari dokumentasi awal atau impresi (Clause 8.5.1).",
                "measures": [
                    {
                        "measure_id": "UAp-1-G",
                        "name": "Description completeness",
                        "description": "What proportion of usage scenarios is described in the product description or user documents?",
                        "formula": "X = A / B (A = Usage scenarios described, B = Total usage scenarios of product)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Review of product documentation & manual",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-4.2",
                "name": "Learnability",
                "description": "Tingkat sejauh mana produk dapat digunakan oleh pengguna untuk mencapai tujuan pembelajaran penggunaan produk (Clause 8.5.2).",
                "measures": [
                    {
                        "measure_id": "ULe-1-G",
                        "name": "User guidance completeness",
                        "description": "What proportion of functions is explained in sufficient detail in user documentation and/or help facility?",
                        "formula": "X = A / B (A = Functions explained in sufficient detail, B = Total functions implemented)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "User guide & contextual help facility audit",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "ULe-3-S",
                        "name": "Error message understandability",
                        "description": "What proportion of the error messages state the reason why the error occurred and how to resolve it?",
                        "formula": "X = A / B (A = Actionable & understandable error messages, B = Total error messages)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Error dialog audit & usability inspection",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-4.3",
                "name": "Operability",
                "description": "Tingkat sejauh mana produk memiliki atribut yang membuatnya mudah dioperasikan dan dikendalikan (Clause 8.5.3).",
                "measures": [
                    {
                        "measure_id": "UOp-1-G",
                        "name": "Operational consistency",
                        "description": "To what extent do interactive tasks have a behaviour and appearance that is consistent both within the task and across similar tasks?",
                        "formula": "X = 1 - A/B (A = Tasks performed inconsistently, B = Tasks that need to be consistent)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "UI design system review & walkthrough",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "UOp-2-G",
                        "name": "Message clarity",
                        "description": "What proportion of messages from a system conveys the right outcome or instructions to the user?",
                        "formula": "X = A / B (A = Clear messages conveying right outcome, B = Total messages implemented)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Heuristic evaluation of notifications and alerts",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "UOp-6-S",
                        "name": "Undo capability",
                        "description": "What proportion of tasks that has a significant consequence provides an option for re-confirmation or undo capability?",
                        "formula": "X = A / B (A = Tasks with undo/confirm prompt, B = Critical tasks benefitting from undo)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Task flow review of destructive actions",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-4.4",
                "name": "User error protection",
                "description": "Tingkat sejauh mana sistem melindungi pengguna dari melakukan kesalahan atau mencegah terjadinya galat (Clause 8.5.4).",
                "measures": [
                    {
                        "measure_id": "UEp-1-G",
                        "name": "Avoidance of user operation error",
                        "description": "What portion of user actions and inputs are protected against causing any system malfunction?",
                        "formula": "X = A / B (A = User actions/inputs protected, B = Total actions that could cause malfunction)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Input validation testing & boundary tests",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "UEp-2-S",
                        "name": "User entry error correction",
                        "description": "To what extent does the system provide a suggested correct value for detected user entry errors with an identifiable cause?",
                        "formula": "X = A / B (A = Errors with suggested correction, B = Total entry errors detected)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Autocomplete & inline form validation testing",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-4.5",
                "name": "User interface aesthetics",
                "description": "Tingkat sejauh mana antarmuka pengguna memungkinkan interaksi yang menyenangkan dan memuaskan bagi pengguna (Clause 8.5.5).",
                "measures": [
                    {
                        "measure_id": "UIn-1-S",
                        "name": "Appearance aesthetics of user interfaces",
                        "description": "To what extent are user interfaces and the overall design aesthetically pleasing in appearance?",
                        "formula": "X = A / B (A = Display interfaces judged pleasing, B = Total display interfaces)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Visual design audit & System Usability Scale (SUS)",
                        "dummy_target": ">= 0.85",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-4.6",
                "name": "Accessibility",
                "description": "Tingkat sejauh mana produk dapat digunakan oleh orang-orang dengan berbagai kemampuan fisik dan karakteristik berbeda (Clause 8.5.6).",
                "measures": [
                    {
                        "measure_id": "UAc-1-G",
                        "name": "Accessibility for users with disabilities",
                        "description": "To what extent can potential users with specific disabilities successfully use the system?",
                        "formula": "X = A / B (A = Functions usable with disability, B = Total functions implemented)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "WCAG 2.1 AA guideline compliance check",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 5,
        "code": "QC-5",
        "name": "Reliability",
        "description": "Tingkat sejauh mana suatu sistem menjalankan fungsi yang ditentukan dalam kondisi tertentu selama periode waktu yang ditentukan (ISO/IEC 25023:2016 Clause 8.6).",
        "subcharacteristics": [
            {
                "code": "QSC-5.1",
                "name": "Maturity",
                "description": "Tingkat sejauh mana suatu sistem memenuhi kebutuhan keandalan dalam operasi normal (Clause 8.6.1).",
                "measures": [
                    {
                        "measure_id": "RMa-1-G",
                        "name": "Fault correction",
                        "description": "What proportion of detected reliability-related faults has been corrected?",
                        "formula": "X = A / B (A = Faults corrected, B = Total reliability faults detected)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Bug tracking & defect resolution audit",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "RMa-2-G",
                        "name": "Mean time between failure (MTBF)",
                        "description": "What is the MTBF during the system/software operation?",
                        "formula": "X = A / B (A = Operation time, B = Number of failures occurred)",
                        "unit": "Jam (hours)",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Operational reliability logging",
                        "dummy_target": ">= 720",
                        "target_unit": "jam"
                    },
                    {
                        "measure_id": "RMa-3-G",
                        "name": "Failure rate",
                        "description": "What is the average number of failures during a defined period?",
                        "formula": "X = A / B (A = Failures detected, B = Duration of observation)",
                        "unit": "Kegagalan/bulan",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Incident reporting monitor",
                        "dummy_target": "<= 1",
                        "target_unit": "kegagalan/bulan"
                    }
                ]
            },
            {
                "code": "QSC-5.2",
                "name": "Availability",
                "description": "Tingkat sejauh mana suatu sistem beroperasi dan dapat diakses saat diperlukan untuk digunakan (Clause 8.6.2).",
                "measures": [
                    {
                        "measure_id": "RAv-1-G",
                        "name": "System availability",
                        "description": "For what proportion of the scheduled system operational time is the system actually available?",
                        "formula": "X = A / B (A = System operation time actually provided, B = Scheduled operation time)",
                        "unit": "Persentase (%)",
                        "direction": "Makin tinggi makin baik (Target = 99.5%)",
                        "verification_method": "Uptime monitor telemetry & SLA report",
                        "dummy_target": ">= 99.5",
                        "target_unit": "%"
                    },
                    {
                        "measure_id": "RAv-2-G",
                        "name": "Mean down time",
                        "description": "How long does the system stay unavailable when a failure occurs?",
                        "formula": "X = A / B (A = Total down time, B = Number of breakdowns observed)",
                        "unit": "Menit",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Incident duration log",
                        "dummy_target": "<= 15",
                        "target_unit": "menit"
                    }
                ]
            },
            {
                "code": "QSC-5.3",
                "name": "Fault tolerance",
                "description": "Tingkat sejauh mana sistem beroperasi sebagaimana dimaksud meskipun terjadi kegagalan perangkat keras atau perangkat lunak (Clause 8.6.3).",
                "measures": [
                    {
                        "measure_id": "RFt-1-G",
                        "name": "Failure avoidance",
                        "description": "What proportion of fault patterns has been brought under control to avoid critical and serious failures?",
                        "formula": "X = A / B (A = Avoided critical failure occurrences, B = Executed fault test cases)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Fault injection testing & exception handling check",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "RFt-2-S",
                        "name": "Redundancy of components",
                        "description": "What proportion of system components is installed redundantly to avoid system failure?",
                        "formula": "X = A / B (A = Components installed redundantly, B = Total system components)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Infrastructure architecture inspection",
                        "dummy_target": ">= 0.50",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-5.4",
                "name": "Recoverability",
                "description": "Tingkat kemampuan memulihkan data yang terkena dampak langsung dan membangun kembali keadaan sistem yang diinginkan setelah kegagalan (Clause 8.6.4).",
                "measures": [
                    {
                        "measure_id": "RRe-1-G",
                        "name": "Mean recovery time",
                        "description": "How long does it take for the software/system to recover from failure?",
                        "formula": "X = Sum(Ai) / n (Ai = Total time to recover downed software for failure i, n = Failures)",
                        "unit": "Menit",
                        "direction": "Makin rendah makin baik",
                        "verification_method": "Disaster recovery drill simulation",
                        "dummy_target": "<= 10",
                        "target_unit": "menit"
                    },
                    {
                        "measure_id": "RRe-2-S",
                        "name": "Backup data completeness",
                        "description": "What proportion of data items is backed up regularly?",
                        "formula": "X = A / B (A = Data items backed up regularly, B = Data items requiring backup)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Automated backup verification test",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 6,
        "code": "QC-6",
        "name": "Security",
        "description": "Tingkat sejauh mana suatu produk melindungi informasi dan data sehingga memiliki tingkat akses data yang sesuai dengan jenis dan tingkat otorisasinya (ISO/IEC 25023:2016 Clause 8.7).",
        "subcharacteristics": [
            {
                "code": "QSC-6.1",
                "name": "Confidentiality",
                "description": "Tingkat sejauh mana suatu produk memastikan bahwa data hanya dapat diakses oleh mereka yang berwenang (Clause 8.7.1).",
                "measures": [
                    {
                        "measure_id": "SCo-1-G",
                        "name": "Access controllability",
                        "description": "What proportion of confidential data items are protected from unauthorized accesses?",
                        "formula": "X = 1 - A/B (A = Confidential data accessed without auth, B = Data requiring access control)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Access control matrix testing & penetration testing",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "SCo-2-G",
                        "name": "Data encryption correctness",
                        "description": "How correctly is the encryption/decryption of data items implemented as stated in the requirement specification?",
                        "formula": "X = A / B (A = Data items encrypted correctly, B = Data items requiring encryption)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Wajib = 1.0)",
                        "verification_method": "Cryptographic inspection (at-rest & in-transit)",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-6.2",
                "name": "Integrity",
                "description": "Tingkat sejauh mana suatu sistem mencegah akses tidak sah atau modifikasi terhadap program atau data (Clause 8.7.2).",
                "measures": [
                    {
                        "measure_id": "SIn-1-G",
                        "name": "Data integrity",
                        "description": "To what extent is the data corruption or modification by unauthorized access prevented?",
                        "formula": "X = 1 - A/B (A = Data corrupted by unauthorized access, B = Data to be protected)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Data tampering test & checksum verification",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "SIn-2-G",
                        "name": "Internal data corruption prevention",
                        "description": "To what extent are the available prevention methods for data corruption implemented?",
                        "formula": "X = A / B (A = Prevention methods implemented, B = Recommended prevention methods)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Database constraint & transaction rollback check",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-6.3",
                "name": "Non-repudiation",
                "description": "Tingkat sejauh mana tindakan atau peristiwa dapat dibuktikan telah terjadi sehingga tidak dapat disangkal (Clause 8.7.3).",
                "measures": [
                    {
                        "measure_id": "SNo-1-G",
                        "name": "Digital signature usage",
                        "description": "What proportion of events requiring non-repudiation is processed using digital signature?",
                        "formula": "X = A / B (A = Events using digital signature, B = Events requiring non-repudiation)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Wajib = 1.0)",
                        "verification_method": "Cryptographic signature validation test",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-6.4",
                "name": "Accountability",
                "description": "Tingkat sejauh mana tindakan suatu entitas dapat ditelusuri secara unik ke entitas tersebut (Clause 8.7.4).",
                "measures": [
                    {
                        "measure_id": "SAc-1-G",
                        "name": "User audit trail completeness",
                        "description": "How complete is the audit trail concerning the user access to the system or data?",
                        "formula": "X = A / B (A = Accesses recorded in logs, B = Total accesses tested)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "SIEM audit log completeness inspection",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-6.5",
                "name": "Authenticity",
                "description": "Tingkat sejauh mana identitas suatu subjek atau sumber daya dapat dibuktikan keasliannya (Clause 8.7.5).",
                "measures": [
                    {
                        "measure_id": "SAu-1-G",
                        "name": "Authentication mechanism sufficiency",
                        "description": "How well does the system authenticate the identity of a subject?",
                        "formula": "X = A / B (A = Authentication mechanisms provided, B = Mechanisms specified)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Multi-factor authentication (MFA) validation",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 7,
        "code": "QC-7",
        "name": "Maintainability",
        "description": "Tingkat efektivitas dan efisiensi produk atau sistem dapat dimodifikasi oleh pemelihara yang dimaksudkan (ISO/IEC 25023:2016 Clause 8.8).",
        "subcharacteristics": [
            {
                "code": "QSC-7.1",
                "name": "Modularity",
                "description": "Tingkat sejauh mana sistem terdiri dari komponen diskrit sehingga perubahan pada satu komponen berdampak minimal pada komponen lain (Clause 8.8.1).",
                "measures": [
                    {
                        "measure_id": "MMo-1-G",
                        "name": "Coupling of components",
                        "description": "How strongly are the components independent and how many components are free from impacts from changes to other components?",
                        "formula": "X = A / B (A = Components with no impact on others, B = Specified independent components)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Architecture dependency analysis & coupling metrics",
                        "dummy_target": ">= 0.85",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "MMo-2-S",
                        "name": "Cyclomatic complexity adequacy",
                        "description": "How many software modules have acceptable cyclomatic complexity?",
                        "formula": "X = 1 - A/B (A = Modules exceeding complexity threshold, B = Total modules)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Static code analysis (McCabe cyclomatic complexity <= 10)",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-7.2",
                "name": "Reusability",
                "description": "Tingkat sejauh mana suatu aset dapat digunakan dalam lebih dari satu sistem atau dalam membangun aset lain (Clause 8.8.2).",
                "measures": [
                    {
                        "measure_id": "MRe-1-G",
                        "name": "Reusability of assets",
                        "description": "How many assets in a system can be reusable?",
                        "formula": "X = A / B (A = Assets designed/implemented to be reusable, B = Total assets in system)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Software asset inventory audit",
                        "dummy_target": ">= 0.30",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-7.3",
                "name": "Analysability",
                "description": "Tingkat efektivitas dan efisiensi menilai dampak perubahan atau mendiagnosis defek/penyebab kegagalan (Clause 8.8.3).",
                "measures": [
                    {
                        "measure_id": "MAn-1-G",
                        "name": "System log completeness",
                        "description": "To what extent does the system record its operations in logs so that they are to be traceable?",
                        "formula": "X = A / B (A = Logs actually recorded, B = Logs required during operation)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Diagnostic log coverage inspection",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "MAn-2-S",
                        "name": "Diagnosis function effectiveness",
                        "description": "What proportion of the diagnosis functions meets the requirements of causal analysis?",
                        "formula": "X = A / B (A = Diagnostic functions useful for causal analysis, B = Diagnostic functions implemented)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Root-cause diagnosis evaluation",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-7.4",
                "name": "Modifiability",
                "description": "Tingkat sejauh mana produk dapat dimodifikasi tanpa menimbulkan defek atau menurunkan kualitas yang ada (Clause 8.8.4).",
                "measures": [
                    {
                        "measure_id": "MMd-1-G",
                        "name": "Modification efficiency",
                        "description": "How efficiently are the modifications made compared to the expected time?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = Work time spent, Bi = Expected time for modification)",
                        "unit": "Indeks efisiensi",
                        "direction": "Makin rendah makin baik (X <= 1.0)",
                        "verification_method": "Maintenance issue tracker time logging",
                        "dummy_target": "<= 1.0",
                        "target_unit": "indeks"
                    },
                    {
                        "measure_id": "MMd-2-G",
                        "name": "Modification correctness",
                        "description": "What proportion of modifications has been implemented correctly?",
                        "formula": "X = 1 - A/B (A = Modifications causing incident/failure, B = Total modifications)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Regression test suite pass rate",
                        "dummy_target": ">= 0.98",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-7.5",
                "name": "Testability",
                "description": "Tingkat efektivitas dan efisiensi kriteria pengujian dapat ditetapkan dan pengujian dapat dilakukan (Clause 8.8.5).",
                "measures": [
                    {
                        "measure_id": "MTe-1-G",
                        "name": "Test function completeness",
                        "description": "How completely are test functions and facilities implemented?",
                        "formula": "X = A / B (A = Test functions implemented as specified, B = Test functions required)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Test suite harness verification",
                        "dummy_target": ">= 0.95",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "MTe-2-S",
                        "name": "Autonomous testability",
                        "description": "How independently can the software be tested?",
                        "formula": "X = A / B (A = Tests simulated by stub, B = Tests depending on other systems)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Mock / stub dependency analysis",
                        "dummy_target": ">= 0.80",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    },
    {
        "iso_number": 8,
        "code": "QC-8",
        "name": "Portability",
        "description": "Tingkat efektivitas dan efisiensi suatu sistem dapat ditransfer dari satu lingkungan perangkat keras, perangkat lunak, atau lingkungan operasional ke lingkungan lain (ISO/IEC 25023:2016 Clause 8.9).",
        "subcharacteristics": [
            {
                "code": "QSC-8.1",
                "name": "Adaptability",
                "description": "Tingkat sejauh mana produk dapat disesuaikan untuk lingkungan perangkat keras, perangkat lunak, atau operasional lain yang berbeda (Clause 8.9.1).",
                "measures": [
                    {
                        "measure_id": "PAd-1-G",
                        "name": "Hardware environmental adaptability",
                        "description": "Is software or system capable enough to adapt itself to different hardware environment?",
                        "formula": "X = 1 - A/B (A = Functions not completed or insufficient, B = Functions tested in different HW)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Multi-hardware compatibility testing",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "PAd-2-G",
                        "name": "System software environmental adaptability",
                        "description": "Is software or system capable enough to adapt itself to different system software environment?",
                        "formula": "X = 1 - A/B (A = Functions insufficient, B = Functions tested in different OS/middleware)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Cross-platform test matrix (Linux and Windows)",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-8.2",
                "name": "Installability",
                "description": "Tingkat efektivitas dan efisiensi suatu produk dapat berhasil dipasang dan/atau dicopot dalam lingkungan tertentu (Clause 8.9.2).",
                "measures": [
                    {
                        "measure_id": "PIn-1-G",
                        "name": "Installation time efficiency",
                        "description": "How efficient is the actual installation time compared to expected time?",
                        "formula": "X = Sum(Ai / Bi) / n (Ai = Total installation work time, Bi = Expected installation time)",
                        "unit": "Indeks efisiensi",
                        "direction": "Makin rendah makin baik (X <= 1.0)",
                        "verification_method": "Installer walkthrough timing test",
                        "dummy_target": "<= 1.0",
                        "target_unit": "indeks"
                    },
                    {
                        "measure_id": "PIn-2-G",
                        "name": "Ease of installation",
                        "description": "Can users or maintainers customize the installation procedure for their convenience?",
                        "formula": "X = A / B (A = Cases user succeeds to customize install, B = Cases customization attempted)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Installation wizard usability testing",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            },
            {
                "code": "QSC-8.3",
                "name": "Replaceability",
                "description": "Tingkat sejauh mana suatu produk dapat menggantikan produk perangkat lunak lain yang ditentukan untuk tujuan yang sama dalam lingkungan yang sama (Clause 8.9.3).",
                "measures": [
                    {
                        "measure_id": "PRe-1-G",
                        "name": "Usage similarity",
                        "description": "What proportion of user functions of the replaced product can be performed without any additional learning or workaround?",
                        "formula": "X = A / B (A = Functions performed without extra learning, B = Functions in replaced product)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik",
                        "verification_method": "Workflow migration evaluation",
                        "dummy_target": ">= 0.90",
                        "target_unit": "rasio"
                    },
                    {
                        "measure_id": "PRe-4-S",
                        "name": "Data reusability/import capability",
                        "description": "Can the same data be used after replacing previous software product by this one?",
                        "formula": "X = A / B (A = Data usable continuously as before, B = Data to be used in replaced product)",
                        "unit": "Rasio [0..1]",
                        "direction": "Makin tinggi makin baik (Optimal = 1.0)",
                        "verification_method": "Database migration & import test",
                        "dummy_target": "= 1.0",
                        "target_unit": "rasio"
                    }
                ]
            }
        ]
    }
]

# FR Characteristics from Table III
FR_CHARACTERISTICS_DATA = [
    {
        "code": "FRC-1",
        "name": "Runs according to the actor",
        "description": "Karakteristik fungsional di mana alur logika dan eksekusi berjalan sesuai interaksi, instruksi, dan hak pengguna/aktor."
    },
    {
        "code": "FRC-2",
        "name": "CRUD / database process",
        "description": "Proses manipulasi data transaksional (Create, Read, Update, Delete), kueri basis data, dan penyimpanan persisten."
    },
    {
        "code": "FRC-3",
        "name": "File transfer",
        "description": "Pengiriman, pengunggahan, pengunduhan, atau pertukaran berkas antar subsistem atau dengan pihak ketiga."
    },
    {
        "code": "FRC-4",
        "name": "Makes tasks easier for users and reduces human error",
        "description": "Fitur interaksi pengguna yang menyediakan panduan, autocomplete, validasi input dini, dan kemudahan navigasi alur tugas."
    },
    {
        "code": "FRC-5",
        "name": "Failure/error detection in the system",
        "description": "Mekanisme pendeteksian galat internal, penanganan exception, failover, atau toleransi terhadap kegagalan komponen sistem."
    },
    {
        "code": "FRC-6",
        "name": "Security of transfers, data, access rights, and controls",
        "description": "Fitur otentikasi identitas, otorisasi peran (RBAC), enkripsi data, dan perlindungan privasi/keamanan data."
    },
    {
        "code": "FRC-7",
        "name": "Module-related functions: reusability, logging, analysis, modification, testability",
        "description": "Fungsi arsitektural modul seperti logging terstruktur, modularitas komponen, kemudahan pengujian, dan kemampuan pemeliharaan."
    },
    {
        "code": "FRC-8",
        "name": "Application configuration and adaptation to other environments, applications, or software",
        "description": "Kemampuan adaptasi aplikasi terhadap berbagai sistem operasi (Linux/Windows), integrasi variabel lingkungan, dan konfigurasi fleksibel."
    }
]

# Sample Indonesian Project & Requirements for Demo
SAMPLE_PROJECT_DATA = {
    "name": "Sistem Informasi Rekam Medis Elektronik (RME) RS Harapan Sehat",
    "description": "Proyek percontohan implementasi sistem manajemen rekam medis digital rumah sakit yang mengintegrasikan pendaftaran pasien, pencatatan resep obat, dan interoperabilitas data kesehatan nasional (SatuSehat).",
    "requirements": [
        {
            "req_code": "FR-001",
            "type": "FR",
            "title": "Autentikasi Pengguna dengan Kontrol Akses Berbasis Peran (RBAC)",
            "description": "Dokter, perawat, dan staf rekam medis wajib login menggunakan NIP dan kata sandi dengan autentikasi multifaktor sebelum mengakses data pasien.",
            "priority": "Critical",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-1", "FRC-6"]
        },
        {
            "req_code": "FR-002",
            "type": "FR",
            "title": "Pencatatan Transaksi Resep Obat dan Pembaruan Stok Farmasi",
            "description": "Sistem mencatat transaksi resep dokter, menghitung dosis obat, dan secara otomatis mengurangi stok inventaris apotek secara real-time.",
            "priority": "High",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-2", "FRC-5"]
        },
        {
            "req_code": "FR-003",
            "type": "FR",
            "title": "Ekspor Data Resume Medis ke Format Standar FHIR SatuSehat",
            "description": "Sistem menyediakan fungsi sinkronisasi dan transfer berkas resume medis pasien dalam format JSON HL7/FHIR ke platform Kementerian Kesehatan.",
            "priority": "High",
            "status": "Under Review",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-3", "FRC-6"]
        },
        {
            "req_code": "FR-004",
            "type": "FR",
            "title": "Pencarian Rekam Medis Pasien dengan Autocomplete dan Validasi Input",
            "description": "Petugas pendaftaran dapat mencari rekam medis menggunakan NIK atau Nomor RM dengan saran otomatis dan pencegahan kesalahan input karakter.",
            "priority": "Medium",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-1", "FRC-4"]
        },
        {
            "req_code": "FR-005",
            "type": "FR",
            "title": "Mekanisme Pemulihan dan Retry Otomatis Koneksi Database",
            "description": "Ketika koneksi database cluster mengalami gangguan sesaat, sistem mendeteksi galat dan melakukan reconnect otomatis hingga 3 kali tanpa crash.",
            "priority": "High",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-5", "FRC-7"]
        },
        {
            "req_code": "FR-006",
            "type": "FR",
            "title": "Konfigurasi Portabel Multi-Platform Berbasis Berkas Konfigurasi",
            "description": "Aplikasi dapat dijalankan di lingkungan Linux maupun Windows dengan membaca parameter koneksi database dan API melalui berkas konfigurasi .env.",
            "priority": "Medium",
            "status": "Draft",
            "mapping_status": "Suggested",
            "fr_characteristics": ["FRC-8"]
        },
        {
            "req_code": "FR-007",
            "type": "FR",
            "title": "Logging Transaksi Sensitif dan Audit Trail Perubahan Medis",
            "description": "Setiap perubahan data diagnosis medis harus dicatat dalam audit trail terstruktur yang mencakup identitas aktor, waktu tepat, dan nilai sebelum-sesudah.",
            "priority": "Critical",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": ["FRC-6", "FRC-7"]
        },
        {
            "req_code": "NFR-001",
            "type": "NFR",
            "title": "Waktu Respon Pemrosesan Kueri Resep Maksimal 300 Milidetik",
            "description": "Operasi pencarian dan penyimpanan transaksi resep obat harus merespons dalam waktu rata-rata di bawah 300 ms pada beban normal.",
            "priority": "High",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": []
        },
        {
            "req_code": "NFR-002",
            "type": "NFR",
            "title": "Ketersediaan Sistem Rawat Inap Minimal 99.5% per Bulan",
            "description": "Sistem pendaftaran dan pemantauan pasien rawat inap harus selalu aktif dengan downtime maksimal 3,6 jam per bulan.",
            "priority": "Critical",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": []
        },
        {
            "req_code": "NFR-003",
            "type": "NFR",
            "title": "Enkripsi Data Pasien Menggunakan AES-256 dan TLS 1.3",
            "description": "Semua data identitas pasien dan riwayat diagnosa harus dienkripsi saat disimpan di basis data dan saat dikirim melalui jaringan.",
            "priority": "Critical",
            "status": "Approved",
            "mapping_status": "Confirmed",
            "fr_characteristics": []
        }
    ]
}
