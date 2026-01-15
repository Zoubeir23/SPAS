import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { studentService } from '@/api/services/studentService'
import { departmentService, programService, type Department, type Program } from '@/api/services/programService'
import type { Student as _StudentType } from '@/api/services/studentService'

interface StudentModalProps {
  isOpen: boolean
  onClose: () => void
  studentId?: string
  onSuccess?: () => void
}

export default function ModaleEtudiant({
  isOpen,
  onClose,
  studentId,
  onSuccess,
}: StudentModalProps) {
  const [loading, setLoading] = useState(false)
  const [uploadingPhoto, setUploadingPhoto] = useState(false)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)
  const [departments, setDepartments] = useState<Department[]>([])
  const [programs, setPrograms] = useState<Program[]>([])
  const [filteredPrograms, setFilteredPrograms] = useState<Program[]>([])
  const [formData, setFormData] = useState<{
    matricule: string
    firstName: string
    lastName: string
    email: string
    phone: string
    dateOfBirth: string
    address: string
    departmentId: string
    programId: string
    programName: string
    level: 'L1' | 'L2' | 'L3' | 'M1' | 'M2'
    scholarship: boolean
  }>({
    matricule: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    address: '',
    departmentId: '',
    programId: '',
    programName: '',
    level: 'L1',
    scholarship: false,
  })

  // Charger les départements et filières
  useEffect(() => {
    if (isOpen) {
      const loadData = async () => {
        try {
          const [depts, progs] = await Promise.all([
            departmentService.getAll({ status: 'active' }),
            programService.getAll({ status: 'active' }),
          ])
          // S'assurer que les données sont des tableaux
          setDepartments(Array.isArray(depts) ? depts : [])
          setPrograms(Array.isArray(progs) ? progs : [])
        } catch (error) {
          console.error('Erreur lors du chargement des départements/filières:', error)
          // Initialiser avec des tableaux vides en cas d'erreur
          setDepartments([])
          setPrograms([])
        }
      }
      loadData()
    } else {
      // Réinitialiser les données quand le modal se ferme
      setDepartments([])
      setPrograms([])
      setFilteredPrograms([])
    }
  }, [isOpen])

  // Filtrer les filières selon le département sélectionné
  useEffect(() => {
    if (formData.departmentId) {
      const filtered = programs.filter(p => p.department_id === formData.departmentId)
      setFilteredPrograms(filtered)
      // Réinitialiser la filière si elle n'appartient pas au nouveau département
      if (formData.programId && !filtered.find(p => p.id === formData.programId)) {
        setFormData(prev => ({ ...prev, programId: '', programName: '' }))
      }
    } else {
      setFilteredPrograms(programs)
    }
  }, [formData.departmentId, programs])

  useEffect(() => {
    if (isOpen && studentId) {
      const loadStudent = async () => {
        const student = await studentService.getById(studentId)
        if (student) {
          // Charger le programme pour obtenir le département
          let departmentId = ''
          if (student.programId) {
            const program = await programService.getById(student.programId)
            if (program?.department_id) {
              departmentId = program.department_id
            }
          }
          setFormData({
            matricule: student.matricule || '',
            firstName: student.firstName || '',
            lastName: student.lastName || '',
            email: student.email || '',
            phone: student.phone || '',
            dateOfBirth: student.dateOfBirth || '',
            address: '',
            departmentId,
            programId: student.programId || '',
            programName: student.programName || '',
            level: 'L1',
            scholarship: false,
          })
          // Charger la photo si disponible
          if (student.photo_url) {
            setPhotoPreview(student.photo_url)
          }
        }
      }
      loadStudent()
    } else if (isOpen) {
      setPhotoPreview(null)
      setFormData({
        matricule: '',
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        dateOfBirth: '',
        address: '',
        departmentId: '',
        programId: '',
        programName: '',
        level: 'L1',
        scholarship: false,
      })
      setPhotoPreview(null)
    }
  }, [isOpen, studentId])

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validation du fichier
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner un fichier image valide')
      return
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB max
      alert('L\'image ne doit pas dépasser 5 Mo')
      return
    }

    setUploadingPhoto(true)

    try {
      // Prévisualisation
      const reader = new FileReader()
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      // Si c'est un étudiant existant, uploader immédiatement
      if (studentId) {
        await studentService.uploadPhoto(studentId, file)
      }
      // Sinon, on garde le fichier pour l'upload lors de la création
    } catch (err: any) {
      console.error('Erreur lors de l\'upload de la photo:', err)
      alert('Erreur lors de l\'upload de la photo')
      setPhotoPreview(null)
    } finally {
      setUploadingPhoto(false)
      event.target.value = ''
    }
  }

  const handlePhotoRemove = () => {
    setPhotoPreview(null)
    // Si c'est un étudiant existant, supprimer la photo
    if (studentId) {
      studentService.update(studentId, { photo: null as any }).catch(err => {
        console.error('Erreur lors de la suppression de la photo:', err)
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (studentId) {
        await studentService.update(studentId, formData)
      } else {
        await studentService.create({
          ...formData,
          sessionId: '1',
          sessionName: 'Automne 2024',
          status: 'active',
        } as any)
      }
      onSuccess?.()
      onClose()
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement:', error)
      alert('Erreur lors de l\'enregistrement')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title="Fiche Étudiant" size="xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Profile Header Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm mb-6 border border-gray-100 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row gap-6 items-center sm:items-start">
            <div className="relative group">
              {photoPreview ? (
                <div className="h-28 w-28 rounded-full overflow-hidden border-4 border-white dark:border-gray-700 shadow-md">
                  <img
                    src={photoPreview}
                    alt={`${formData.firstName} ${formData.lastName}`}
                    className="h-full w-full object-cover"
                  />
                </div>
              ) : (
                <div className="h-28 w-28 rounded-full overflow-hidden border-4 border-white dark:border-gray-700 shadow-md bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                  <span className="material-symbols-outlined text-5xl text-gray-400">person</span>
                </div>
              )}
            </div>
            <div className="flex flex-col justify-center text-center sm:text-left flex-1">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Photo de profil</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1 mb-3">
                Formats acceptés: JPG, PNG (Max 5Mo). Une photo professionnelle aide à
                l'identification.
              </p>
              <div className="flex gap-3 justify-center sm:justify-start">
                <label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    className="hidden"
                    disabled={uploadingPhoto}
                  />
                  <Bouton type="button" variant="outline" size="sm" disabled={uploadingPhoto}>
                    {uploadingPhoto ? (
                      <>
                        <span className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full mr-2"></span>
                        Upload...
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-[18px] mr-2">upload</span>
                        Télécharger
                      </>
                    )}
                  </Bouton>
                </label>
                {photoPreview && (
                  <Bouton
                    type="button"
                    variant="outline"
                    size="sm"
                    className="text-red-600 border-red-300 hover:bg-red-50"
                    onClick={handlePhotoRemove}
                    disabled={uploadingPhoto}
                  >
                    Supprimer
                  </Bouton>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Personal Information Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm mb-6 border border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-5 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-800">
            <span className="material-symbols-outlined text-gray-400">person</span>
            Informations Personnelles
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="col-span-1 md:col-span-2">
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Matricule <span className="text-red-600">*</span>
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">badge</span>
                </div>
                <ChampSaisie
                  required
                  className="pl-11"
                  placeholder="Ex: 20230156"
                  value={formData.matricule}
                  onChange={(e) => setFormData({ ...formData, matricule: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Nom <span className="text-red-600">*</span>
              </label>
              <ChampSaisie
                required
                placeholder="Nom de famille"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Prénom <span className="text-red-600">*</span>
              </label>
              <ChampSaisie
                required
                placeholder="Prénom(s)"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Date de naissance <span className="text-red-600">*</span>
              </label>
              <ChampSaisie
                required
                type="date"
                value={formData.dateOfBirth}
                onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Genre
              </label>
              <select
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-3 px-4 pr-10 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm transition-all"
              >
                <option>Sélectionner</option>
                <option>Masculin</option>
                <option>Féminin</option>
                <option>Autre</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Email <span className="text-red-600">*</span>
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">mail</span>
                </div>
                <ChampSaisie
                  required
                  type="email"
                  className="pl-11"
                  placeholder="etudiant@ecole.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Téléphone
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">call</span>
                </div>
                <ChampSaisie
                  type="tel"
                  className="pl-11"
                  placeholder="+33 6 12 34 56 78"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
            </div>

            <div className="col-span-1 md:col-span-2">
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Adresse Complète
              </label>
              <textarea
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-3 px-4 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm resize-none transition-all"
                rows={2}
                placeholder="Numéro, Rue, Ville, Code Postal"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Academic Information Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-5 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-800">
            <span className="material-symbols-outlined text-gray-400">school</span>
            Informations Académiques
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Département <span className="text-red-600">*</span>
              </label>
              <select
                required
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-3 px-4 pr-10 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm transition-all"
                value={formData.departmentId}
                onChange={(e) => setFormData({ ...formData, departmentId: e.target.value, programId: '', programName: '' })}
              >
                <option value="">Sélectionner un département</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Filière <span className="text-red-600">*</span>
              </label>
              <select
                required
                disabled={!formData.departmentId}
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-3 px-4 pr-10 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                value={formData.programId}
                onChange={(e) => {
                  const selectedProgram = filteredPrograms.find(p => p.id === e.target.value)
                  setFormData({ 
                    ...formData, 
                    programId: e.target.value, 
                    programName: selectedProgram?.name || '' 
                  })
                }}
              >
                <option value="">{formData.departmentId ? 'Sélectionner une filière' : 'Sélectionnez d\'abord un département'}</option>
                {filteredPrograms.map((program) => (
                  <option key={program.id} value={program.id}>
                    {program.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2.5">
                Niveau <span className="text-red-600">*</span>
              </label>
              <select
                required
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-3 px-4 pr-10 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm transition-all"
                value={formData.level}
                onChange={(e) => setFormData({ ...formData, level: e.target.value as 'L1' | 'L2' | 'L3' | 'M1' | 'M2' })}
              >
                <option value="L1">Licence 1</option>
                <option value="L2">Licence 2</option>
                <option value="L3">Licence 3</option>
                <option value="M1">Master 1</option>
                <option value="M2">Master 2</option>
              </select>
            </div>

            <div className="col-span-1 md:col-span-2 flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <div className="flex flex-col">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  Statut Boursier
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Cet étudiant bénéficie-t-il d'une bourse d'études ?
                </span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.scholarship}
                  onChange={(e) => setFormData({ ...formData, scholarship: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton type="button" variant="outline" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            <span className="material-symbols-outlined text-[20px] mr-2">save</span>
            Enregistrer
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

