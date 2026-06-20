import json
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.agent_base import AgentBase
from shared.path_guard import PathGuard


class VentureGenerator(AgentBase):
    """Agent 1: Read source data, expand venture tree, write updated ventures.json."""

    def __init__(self, data_root: str = '/data'):
        super().__init__('venture-generator', data_root)
        self.path_guard = PathGuard()

    def run(self, ventures_data: dict, conversation_context: str = '') -> dict:
        self.increment()
        result = {
            'groups_processed': 0,
            'ventures_created': 0,
            'offerings_created': 0,
            'errors': [],
        }

        try:
            # Validate input
            if 'groups' not in ventures_data:
                raise ValueError('Missing groups in ventures data')

            # Process each group
            for group in ventures_data.get('groups', []):
                if self.should_stop():
                    result['errors'].append(self.get_stop_reason())
                    break

                self.increment()
                group_id = group.get('id', '')
                group_name = group.get('name', '')

                # Ensure group has required fields
                if not group.get('mission'):
                    group['mission'] = f'Mission for {group_name}'

                # Ensure slug
                if not group.get('slug'):
                    group['slug'] = group_id

                result['groups_processed'] += 1

                # Process ventures in this group
                for venture in ventures_data.get('ventures', []):
                    if venture.get('parentId') != group_id:
                        continue

                    if self.should_stop():
                        break

                    self.increment()
                    venture_id = venture.get('id', '')

                    # Ensure venture has required fields
                    if not venture.get('mission'):
                        venture['mission'] = f'Mission for {venture.get("name", venture_id)}'
                    if not venture.get('slug'):
                        venture['slug'] = venture_id
                    if not venture.get('type'):
                        venture['type'] = 'venture'

                    result['ventures_created'] += 1

                    # Process offerings
                    for offering in venture.get('offerings', []):
                        if self.should_stop():
                            break
                        self.increment()
                        if not offering.get('slug'):
                            offering['slug'] = offering.get('id', '')
                        if not offering.get('type'):
                            offering['type'] = 'offering'
                        result['offerings_created'] += 1

            # Update metadata
            ventures_data['version'] = '2.0'
            ventures_data['generated_by'] = self.agent_name
            ventures_data['run_id'] = self.run_id

            result['success'] = True
            result['ventures_data'] = ventures_data

        except Exception as e:
            self.emit_failure(e, {'groups': len(ventures_data.get('groups', []))})
            result['errors'].append(str(e))
            result['success'] = False

        return result

    def validate_output(self, ventures_data: dict) -> dict:
        errors = []
        for group in ventures_data.get('groups', []):
            if not group.get('id'):
                errors.append('Group missing id')
            if not group.get('name'):
                errors.append(f"Group '{group.get('id')}' missing name")
            if not group.get('slug'):
                errors.append(f"Group '{group.get('id')}' missing slug")
            if not group.get('mission'):
                errors.append(f"Group '{group.get('id')}' missing mission")

        for venture in ventures_data.get('ventures', []):
            if not venture.get('id'):
                errors.append('Venture missing id')
            if not venture.get('parentId'):
                errors.append(f"Venture '{venture.get('id')}' missing parentId")

        return {'valid': len(errors) == 0, 'errors': errors}
