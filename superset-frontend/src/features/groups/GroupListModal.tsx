/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { t } from '@apache-superset/core/translation';
import { useToasts } from 'src/components/MessageToasts/withToasts';
import { ModalTitleWithIcon } from 'src/components/ModalTitleWithIcon';
import { GroupObject } from 'src/pages/GroupsList';
import {
  FormItem,
  FormModal,
  Input,
  Select,
  AsyncSelect,
} from '@superset-ui/core/components';
import { getUserDisplayLabel } from 'src/features/users/utils';
import { handleFormModalSubmit } from 'src/views/CRUD/utils';
import { FormValues, GroupModalProps } from './types';
import { createGroup, fetchUserOptions, updateGroup } from './utils';

function GroupListModal({
  show,
  onHide,
  onSave,
  roles,
  isEditMode = false,
  group,
}: GroupModalProps) {
  const { addDangerToast, addSuccessToast } = useToasts();
  const handleFormSubmit = async (values: FormValues) => {
    if (isEditMode && !group) {
      throw new Error('Group is required in edit mode');
    }
    return handleFormModalSubmit({
      isEditMode,
      createFn: async (v: FormValues) => {
        await createGroup(v);
      },
      updateFn: async (v: FormValues) => {
        await updateGroup(group!.id, v);
      },
      values,
      addSuccessToast,
      addDangerToast,
      entityName: t('group'),
      duplicateKeyHandlers: {
        ab_group_name_key: t(
          'This name is already taken. Please choose another one.',
        ),
      },
    });
  };

  const requiredFields = ['name'];
  const initialValues = {
    ...group,
    roles: group?.roles?.map(role => role.id) || [],
    users:
      group?.users?.map(user => ({
        value: user.id,
        label: getUserDisplayLabel(user),
      })) || [],
  };

  return (
    <FormModal
      show={show}
      onHide={onHide}
      name={isEditMode ? 'Edit Group' : 'Add Group'}
      title={
        <ModalTitleWithIcon
          isEditMode={isEditMode}
          title={isEditMode ? t('Edit Group') : t('Add Group')}
        />
      }
      onSave={onSave}
      formSubmitHandler={handleFormSubmit}
      requiredFields={requiredFields}
      initialValues={initialValues}
    >
      <FormItem
        name="name"
        label={t('Name')}
        rules={[{ required: true, message: t('Name is required') }]}
      >
        <Input name="name" placeholder={t("Enter the group's name")} />
      </FormItem>
      <FormItem name="label" label={t('Label')}>
        <Input name="label" placeholder={t("Enter the group's label")} />
      </FormItem>
      <FormItem name="description" label={t('Description')}>
        <Input
          name="description"
          placeholder={t("Enter the group's description")}
        />
      </FormItem>
      <FormItem name="roles" label={t('Roles')}>
        <Select
          name="roles"
          mode="multiple"
          placeholder={t('Select roles')}
          options={roles.map(role => ({
            value: role.id,
            label: role.name,
          }))}
          getPopupContainer={trigger => trigger.closest('.ant-modal-content')}
        />
      </FormItem>
      <FormItem name="users" label={t('Users')}>
        <AsyncSelect
          name="users"
          mode="multiple"
          placeholder={t('Select users')}
          options={(filterValue, page, pageSize) =>
            fetchUserOptions(filterValue, page, pageSize, addDangerToast)
          }
        />
      </FormItem>
    </FormModal>
  );
}

export const GroupListAddModal = (
  props: Omit<GroupModalProps, 'isEditMode' | 'initialValues'>,
) => <GroupListModal {...props} isEditMode={false} />;

export const GroupListEditModal = (
  props: Omit<GroupModalProps, 'isEditMode'> & { group: GroupObject },
) => <GroupListModal {...props} isEditMode />;

export default GroupListModal;
